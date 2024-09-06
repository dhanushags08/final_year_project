const express = require("express");
const { User } = require('./db');
const cors=require('cors');
const axios = require('axios');
const multer = require('multer');
const FormData = require('form-data');
const app=express();
app.use(express.json())
const fs = require('fs');
app.use(cors())
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
      cb(null, 'uploads/'); // Specify the directory where uploaded files will be stored
    },
    filename: function (req, file, cb) {
      cb(null, file.originalname); // Keep the original filename
    }
});
const accountSid = 'AC5a594e07b607fdd2b367907d602d7977';
const authToken = 'a5dbc1284058a2b798a190bdab74401b';
const client = require('twilio')(accountSid, authToken);
  
const upload = multer({ storage: storage });
app.post('/addNumberPlate',async (req,res)=>{
    let numberplateDetails=req.body;
    console.log(numberplateDetails);
    let user=(await User.find(numberplateDetails)).length;
    console.log(user);
    if(!user){
        let plate=new User(numberplateDetails);
        await plate.save();
        
        const message = await client.messages
        .create({
            body: 'Your caught without helmet and pay fine of Rs.500 '+numberplateDetails.numberplate,
             from: '+17194273737',
            to: '+919912860955'
        })
        console.log(`Message SID: ${message.sid}`);
    res.json({ status: 'success', msg: 'Message sent successfully!' ,r:1});
    }
    else
    res.json({
        msg:"Already exists",
        r:0
    })
})
app.post('/predict', upload.single('video'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No video file provided' });
        }
        
        const form = new FormData();
        // console.log(req.file.path)
        form.append('video', fs.createReadStream(req.file.path));
        // console.log(form.getHeaders())
        // console.log(form)
        const response = await axios.post('http://127.0.0.1:5002/process_video', form, {
            headers: {
                ...form.getHeaders()
            },
            responseType: "stream",
        });
        console.log("RESPONSE");
        // console.log(response);
        response.data.pipe(res);
    } catch (error) {
        console.error("Error predicting:", error);
        res.status(500).json({ error: error.toString() });
    }
});


  
app.listen(3000, () => console.log('Server running on port 3000'))
