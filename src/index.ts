import express from 'express';
import cors from 'cors';
import derivative from './routes/derivative';
import integral from './routes/integral';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

app.use("/derivative", derivative);
app.use("/integral", integral);

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});