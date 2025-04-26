// backend/index.js

require("dotenv").config();
const express = require("express");
const cors = require("cors");
const axios = require("axios");
const multer = require("multer");
const FormData = require("form-data");
const fs = require("fs");
const { User } = require("./db");
const client = require("twilio")(
  process.env.TWILIO_SID,
  process.env.TWILIO_TOKEN
);

const app = express();
app.use(express.json());
app.use(cors());

// Multer setup for video uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, "uploads/"),
  filename: (req, file, cb) => cb(null, Date.now() + "-" + file.originalname),
});
const upload = multer({ storage });

// Helper: count SMS sent today for rate limiting
function countSmsToday(log) {
  const startOfDay = new Date();
  startOfDay.setHours(0, 0, 0, 0);
  return log.filter((ts) => ts >= startOfDay).length;
}

// Endpoint: add a number plate and notify (max 5 SMS per calendar day)
app.post("/addNumberPlate", async (req, res) => {
  try {
    const { numberplate, email, phonenumber } = req.body;
    const now = new Date();

    // Find existing record
    let user = await User.findOne({ numberplate, email, phonenumber });

    if (!user) {
      // New record: create with initial SMS log entry
      user = new User({ numberplate, email, phonenumber, smsLog: [now] });
      await user.save();
    } else {
      // Existing record: enforce daily SMS limit
      const sentToday = countSmsToday(user.smsLog);
      if (sentToday >= 5) {
        return res.json({
          status: "limit_reached",
          msg: "Max 5 SMS sent today",
        });
      }
      // Append new timestamp and save
      user.smsLog.push(now);
      await user.save();
    }

    // Send SMS via Twilio
    const message = await client.messages.create({
      body: `Traffic violation: no helmet detected. Plate: ${numberplate}.`,
      from: process.env.TWILIO_FROM_PHONE,
      to: phonenumber,
    });
    console.log(`SMS sent, SID: ${message.sid}`);

    return res.json({
      status: "success",
      msg: "Notification sent",
      sid: message.sid,
    });
  } catch (err) {
    console.error("Error in /addNumberPlate:", err);
    return res.status(500).json({ error: err.message });
  }
});

// Endpoint: process video through detector service
app.post("/predict", upload.single("video"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "No video file provided" });
    }

    const detectorUrl =
      process.env.DETECTOR_URL_VIDEO || "http://localhost:5003/process_video";

    const form = new FormData();
    form.append("video", fs.createReadStream(req.file.path));

    const response = await axios.post(detectorUrl, form, {
      headers: form.getHeaders(),
      responseType: "stream",
    });

    response.data.pipe(res);
  } catch (err) {
    console.error("Error in /predict:", err);
    res.status(500).json({ error: err.message });
  }
});

// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Backend running on port ${PORT}`));
