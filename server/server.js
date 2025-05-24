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
      await fs.appendFile('data.txt', JSON.stringify(data) + '\n');
      res.json({ message: 'Data saved successfully' });  // <-- here
    } catch (error) {
      console.error(error);
      res.status(500).json({ error: 'Error saving data' });  // send JSON on error too
    }
  });

app.get('/data', async (req, res) => {
    try {
        const fileData = await fs.readFile('data.txt', 'utf8');
        const lines = fileData.split('\n').filter(Boolean);
        const jsonObjects = lines.map((line, index) => {
            try {
                return JSON.parse(line);
            } catch {
                return { error: `Invalid JSON on line ${index + 1}`, raw: line };
            }
        });
        res.json(jsonObjects);
    } catch (error) {
        console.error(error);
        res.status(500).send('Error reading data');
    }
});


app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});

