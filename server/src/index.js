import dotenv from "dotenv";
dotenv.config({ path: "./config.env" });
import app from "./app.js";
import connectDB from "./db/index.js";

connectDB()
  .then(() => {
    app.on("error", (err) => {
      console.log("Server error: ", err);
      throw err;
    });
    app.listen(process.env.PORT || 8010, () => {
      console.log(`Server running on ${process.env.PORT}`);
    });
  })
  .catch((err) => {
    console.log("MONGODB connection failed", err);
  });
