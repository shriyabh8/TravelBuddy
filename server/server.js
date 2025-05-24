const express = require('express');
const fs = require('fs').promises;
const cors = require('cors');
const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

app.post('/submit', async (req, res) => {
    try {
    const data = req.body;
    await fs.appendFile('data.csv', JSON.stringify(data) + '\n');
    res.send('Data saved successfully');
    } catch (error) {
    console.error(error);
    res.status(500).send('Error saving data');
    }
});

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});