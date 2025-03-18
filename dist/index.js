"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const express_rate_limit_1 = __importDefault(require("express-rate-limit"));
const derivative_1 = __importDefault(require("./routes/derivative"));
const integral_1 = __importDefault(require("./routes/integral"));
const dotenv_1 = __importDefault(require("dotenv"));
const path_1 = __importDefault(require("path"));
dotenv_1.default.config({ path: path_1.default.resolve(__dirname, '.env') });
// console.log('Loaded .env, FRONTEND_URL =', process.env.FRONTEND_URL);
const app = (0, express_1.default)();
const PORT = parseInt(process.env.PORT || '8080', 10);
const NODE_ENV = process.env.NODE_ENV || 'development';
const allowedOrigins = [
    process.env.FRONTEND_URL || "http://192.168.1.106:3000",
    "http://localhost:3000"
];
console.log(`Environment: ${NODE_ENV}`);
console.log(`Allowed origins: ${allowedOrigins}`);
app.set('trust proxy', 1);
app.use((0, helmet_1.default)());
const limiter = (0, express_rate_limit_1.default)({
    windowMs: 15 * 60 * 1000,
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
});
app.use(limiter);
const corsOptions = {
    origin: (origin, callback) => {
        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true);
        }
        else {
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
app.use((0, cors_1.default)(corsOptions));
app.use(express_1.default.json());
if (NODE_ENV === 'production') {
    app.use((req, res, next) => {
        if (!req.secure && req.headers['x-forwarded-proto'] !== 'https') {
            return res.redirect('https://' + req.headers.host + req.url);
        }
        next();
    });
}
app.use("/derivative", derivative_1.default);
app.use("/integral", integral_1.default);
const errorHandler = (err, _req, res, _next) => {
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
