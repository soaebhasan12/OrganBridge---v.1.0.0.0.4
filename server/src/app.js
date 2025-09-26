import express from "express";
import cors from "cors";
import cookieparser from "cookie-parser";

const app = express();

app.use(
  express.json({
    limit: "20mb",
  })
);

app.use(cookieparser());

app.use(
  cors({
    credentials: true,
    origin: process.env.CORS_ORIGIN,
  })
);

console.log("CORS_ORIGIN:", process.env.CORS_ORIGIN); // Debug this

// app.use(express.static('public'));

app.use(
  express.urlencoded({
    extended: true,
    limit: "20mb",
  })
);

export default app;