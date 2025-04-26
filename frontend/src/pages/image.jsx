// frontend/src/pages/Image.jsx
import React, { useState, useEffect } from "react";
import { useRecoilState, useRecoilValue } from "recoil";
import { imageState, processedImageState } from "../atoms/processedVideo";
import axios from "axios";

export function Image() {
  const file = useRecoilValue(imageState);
  const [processedImage, setProcessedImage] =
    useRecoilState(processedImageState);
  const [numberPlate, setNumberPlate] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!file) return; // wait until file is set

    const detectTrafficViolation = async () => {
      try {
        const formData = new FormData();
        formData.append("image", file);

        const response = await axios.post(
          "http://localhost:5003/detect",
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );

        setProcessedImage(response.data.image);
        setNumberPlate(response.data.number_plate_text);
      } catch (error) {
        console.error("Error detecting image:", error);
      }
    };

    detectTrafficViolation();
  }, [file, setProcessedImage]);

  const sendChallan = async () => {
    try {
      const res = await axios.post(
        "http://localhost:3000/addNumberPlate",
        {
          numberplate: numberPlate,
          email: "user@example.com",
          phonenumber: "+919912860955",
        },
        { headers: { "Content-Type": "application/json" } }
      );
      setMessage(res.data.msg);
    } catch (error) {
      console.error("Error sending challan:", error);
      setMessage("Failed to send challan");
    }
  };

  if (!file) {
    return <p className="text-center mt-8">Please select an image first.</p>;
  }

  return (
    <div className="flex flex-col items-center p-4">
      {processedImage && (
        <img
          src={`data:image/jpeg;base64,${processedImage}`}
          alt="Processed"
          className="mb-4 max-w-full rounded"
        />
      )}
      <p className="font-bold mb-4">Plate: {numberPlate}</p>
      <button
        onClick={sendChallan}
        className="bg-red-500 text-white px-4 py-2 rounded mb-2"
      >
        Send E-Challan
      </button>
      {message && <p className="mt-2 text-green-600">{message}</p>}
    </div>
  );
}
