const mysql = require("mysql2/promise");
const connection = require("../database");

const formularioController = {
  createFormulario: async (req, res) => {
    console.log("caca");
    try {
      // Obtén el número de atención dinámicamente del cuerpo de la solicitud
      console.log(req.body);
      const numeroAtencion = Object.keys(req.body)[0];

      // Parsea los datos del cuerpo de la solicitud para obtener la información necesaria
      const formData = req.body[numeroAtencion][0];
      console.log(formData);
      // Extrae los datos específicos
      const {
        CNE,
        bienRaiz,
        enajenantes,
        adquirentes,
        fojas,
        fechaInscripcion,
        nroInscripcion,
      } = formData;
      const { comuna, manzana, predio } = bienRaiz;

      // Construye la consulta SQL para insertar los datos
      const sql = `
        INSERT INTO Formulario 
          (numero_atencion, cne, comuna, manzana, predio, fojas, fecha_inscripcion, numero_inscripcion) 
        VALUES 
          (?, ?, ?, ?, ?, ?, ?, ?)
      `;

      // Ejecuta la consulta SQL
      const connection = await mysql.createConnection({
        host: "flask-g19-miuandes-3b9d.a.aivencloud.com",
        user: "avnadmin",
        password: "AVNS_LHyyUux2JxRT64CsmA5",
        database: "defaultdb",
        port: 18573,
      });
      const [result] = await connection.query(sql, [
        numeroAtencion, // Utiliza el número de atención dinámicamente obtenido
        CNE,
        comuna,
        manzana,
        predio,
        fojas,
        fechaInscripcion,
        nroInscripcion,
      ]);

      // Envía una respuesta exitosa
      res.json({ msg: "Formulario creado exitosamente", result });
    } catch (error) {
      // Envía un mensaje de error si ocurre algún problema
      res.status(500).json({ msg: error.message });
    }
  },
};

module.exports = formularioController;
