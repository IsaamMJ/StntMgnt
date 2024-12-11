const express = require('express');
const multer = require('multer');
const { Storage } = require('@google-cloud/storage');
const path = require('path');

// Initialize Express app
const app = express();
const port = 3000;

// Set up Multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Initialize Google Cloud Storage
const gcs = new Storage();
const bucketName = '06_stntmgntmodule1'; // Replace with your GCS bucket name
const bucket = gcs.bucket(bucketName);

// Serve static files (like the HTML page)
app.use(express.static('public'));

// Endpoint for handling file upload
app.post('/upload', upload.single('csvFile'), (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file uploaded.');
    }

    // Create a blob in the GCS bucket
    const blob = bucket.file(req.file.originalname);
    const blobStream = blob.createWriteStream();

    // Pipe the file to GCS
    blobStream.on('error', (err) => {
        console.log(err);
        res.status(500).send('Error uploading file to GCS');
    });

    blobStream.on('finish', () => {
        // Make the file publicly accessible (optional)
        blob.makePublic().then(() => {
            res.status(200).send(`File uploaded successfully. Accessible at: https://storage.googleapis.com/${bucketName}/${req.file.originalname}`);
        });
    });

    blobStream.end(req.file.buffer);
});

// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
