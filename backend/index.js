const express = require("express");
const connection = require("./database");
const cors = require("cors");
const app = express();
const PORT = process.env.PORT;
const tablasRouter = require("./routes/tablas.router");
// Ruta de prueba
app.use(cors());
app.use("/tablas/", tablasRouter);
app.get("/", (req, res) => {
  res.send("¡Hola, mundo! prueba 1");
});
app.listen(5000, () => {
  console.log(`Servidor escuchando en http://localhost:5000`);
});
