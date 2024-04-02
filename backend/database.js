const mysql = require("mysql");

// Configuración de la conexión a la base de datos
const connection = mysql.createConnection({
  host: "sql107.infinityfree.com",
  user: "if0_36289234",
  password: "7vtj09k4",
  database: "if0_36289234_g19flask1",
});

// Establecer conexión a la base de datos
connection.connect((err) => {
  if (err) {
    console.error("Error al conectar a la base de datos:", err);
    return;
  }
  console.log("Conexión a la base de datos establecida");
});

module.exports = connection;
