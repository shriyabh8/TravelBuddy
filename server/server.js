const express = require('express');
const fs = require('fs').promises;
const cors = require('cors');
const app = express();
const port = 3000;
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

app.use(cors());
app.use(express.json());

app.post('/submit', async (req, res) => {
    try {
      const data = req.body;
      await fs.appendFile('form-data.txt', JSON.stringify(data) + '\n');
      res.json({ message: 'Data saved successfully' });  // <-- here
    } catch (error) {
      console.error(error);
      res.status(500).json({ error: 'Error saving data' });  // send JSON on error too
    }
  });



app.get('/data', async (req, res) => {
    try {
        const fileData = await fs.readFile('form-data.txt', 'utf8');
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

app.post('/itinerary-submit', async (req, res) => {
    try {
      const data = req.body;
      await fs.appendFile('itinerary-data.txt', JSON.stringify(data) + '\n');
      res.json({ message: 'Data saved successfully' });  // <-- here
    } catch (error) {
      console.error(error);
      res.status(500).json({ error: 'Error saving data' });  // send JSON on error too
    }
  });

  app.get('/itinerary-data', async (req, res) => {
    try {
      // Run the Python script that reads form-data.txt and writes itinerary-data.txt
      await execPromise('python3 listener.py');
  
      // After python finishes, read itinerary-data.txt
      const fileData = await fs.readFile('itinerary-data.txt', 'utf8');
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
      res.status(500).json({ error: 'Error processing itinerary data' });
    }
  });


app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
