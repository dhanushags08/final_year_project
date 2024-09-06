const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost:27017/mlProject');
let UserSchema = new mongoose.Schema({
    numberplate: {
        type: String,
        required: true,
    },
    email: {
        type: String,
        required: true
    },
    phonenumber: {
        type: String,
        required: true
    }
});
let User = mongoose.model('UserTable', UserSchema);
module.exports = {
    User
};
