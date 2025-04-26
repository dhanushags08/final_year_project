// db.js
const mongoose = require("mongoose");
require("dotenv").config();

console.log(
  "Attempting to connect to MongoDB with URI:",
  process.env.MONGO_URI
);

mongoose
  .connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log("Connected to MongoDB successfully"))
  .catch((err) => console.error("MongoDB connection error:", err.message));

const UserSchema = new mongoose.Schema({
  numberplate: {
    type: String,
    required: true,
  },
  email: {
    type: String,
    required: true,
  },
  phonenumber: {
    type: String,
    required: true,
  },
});

const User = mongoose.model("UserTable", UserSchema);

module.exports = { User };
