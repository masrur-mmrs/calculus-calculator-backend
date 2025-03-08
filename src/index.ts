import express, { Request, Response, NextFunction, ErrorRequestHandler } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import derivative from './routes/derivative';
import integral from './routes/integral';
import dotenv from "dotenv";
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '.env') });
// console.log('Loaded .env, FRONTEND_URL =', process.env.FRONTEND_URL);

const app = express();
const PORT = parseInt(process.env.PORT || '8080', 10);
const NODE_ENV = process.env.NODE_ENV || 'development';

const allowedOrigins = [
  process.env.FRONTEND_URL || "http://192.168.1.106:3000", 
  "http://localhost:3000"
];

console.log(`Environment: ${NODE_ENV}`);
console.log(`Allowed origins: ${allowedOrigins}`);

app.set('trust proxy', 1);

app.use(helmet());

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

const corsOptions: cors.CorsOptions = {
  origin: (origin: string | undefined, callback: (err: Error | null, allow?: boolean) => void) => {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      const msg = `The origin ${origin} is not allowed by CORS`;
      console.error(msg);
      callback(new Error(msg));
    }
  },
  methods: ["GET", "POST"],
  allowedHeaders: ["Content-Type", "Authorization"],
  credentials: true,
  maxAge: 86400,
};

app.use(cors(corsOptions));

app.use(express.json());

if (NODE_ENV === 'production') {
  app.use((req: Request, res: Response, next: NextFunction) => {
    if (!req.secure && req.headers['x-forwarded-proto'] !== 'https') {
      return res.redirect('https://' + req.headers.host + req.url);
    }
    next();
  });
}

app.use("/derivative", derivative);
app.use("/integral", integral);

const errorHandler: ErrorRequestHandler = (err, _req, res, _next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Server error', 
    message: NODE_ENV === 'development' ? err.message : 'An unexpected error occurred'
  });
};

app.use(errorHandler);

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
  console.log(`Node environment: ${NODE_ENV}`);
});
