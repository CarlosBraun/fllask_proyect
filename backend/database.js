const mysql = require("mysql2");

// Configuración de la conexión a la base de datos
const connection = mysql.createConnection({
  host: "flask-g19-miuandes-3b9d.a.aivencloud.com",
  user: "avnadmin",
  password: "AVNS_LHyyUux2JxRT64CsmA5",
  database: "defaultdb",
  port: "18573",
});

// Establecer conexión a la base de datos
connection.connect((err) => {
  if (err) {
    console.error("Error al conectar a la base de datos:", err);
    return;
  }
  console.log(
    "Conexión a la base de datos establecida a flask-g19-miuandes-3b9d.a.aivencloud.com"
  );
});

module.exports = connection;
