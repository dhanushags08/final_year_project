// index.js
require("dotenv").config();
const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const axios = require("axios");
const multer = require("multer");
const FormData = require("form-data");
const fs = require("fs");
const { User } = require("./db"); // ensure db.js exports a User model

const app = express();
app.use(express.json());
app.use(cors());

// MongoDB connection
mongoose
  .connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log("MongoDB connected"))
  .catch((err) => console.error("MongoDB connection error:", err));

// Twilio client
const client = require("twilio")(
  process.env.TWILIO_SID,
  process.env.TWILIO_TOKEN
);

// Multer setup for handling uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, "uploads/"),
  filename: (req, file, cb) => cb(null, Date.now() + "-" + file.originalname),
});
const upload = multer({ storage });

// Endpoint: add a number plate and notify
app.post("/addNumberPlate", async (req, res) => {
  try {
    const details = req.body;
    const exists = await User.exists(details);
    if (!exists) {
      const plate = new User(details);
      await plate.save();

      // Send SMS
      const message = await client.messages.create({
        body: `Traffic violation: no helmet detected. Plate: ${details.numberplate}. Fine: Rs.500`,
        from: process.env.TWILIO_FROM_PHONE,
        to: details.phone, // pass recipient in request
      });
      console.log(`SMS sent, SID: ${message.sid}`);

      return res.json({
        status: "success",
        msg: "Notification sent",
        sid: message.sid,
      });
    } else {
      return res.json({ status: "duplicate", msg: "Record already exists" });
    }
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
      process.env.DETECTOR_URL || "http://localhost:5003/detect";
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
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Backend running on port ${PORT}`));
