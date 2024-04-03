const mysql = require("mysql2/promise");
const connection = require("../database");

const busquedaController = {
  busqueda: async (req, res) => {
    try {
      const { comuna, manzana, predio, año } = req.body;

      // Obtiene una nueva conexión
      const connection = await mysql.createConnection({
        host: "flask-g19-miuandes-3b9d.a.aivencloud.com",
        user: "avnadmin",
        password: "AVNS_LHyyUux2JxRT64CsmA5",
        database: "defaultdb",
        port: 18573,
      });

      // Consulta para obtener la información del formulario
      const formularioSQL = `
        SELECT * FROM Formulario
        WHERE comuna = ? AND manzana = ? AND predio = ? OR YEAR(fecha_inscripcion) = ?
      `;
      const [formularioRows] = await connection.query(formularioSQL, [
        comuna,
        manzana,
        predio,
        año,
      ]);
      const formulario = formularioRows[0];

      if (!formulario) {
        return res.status(404).json({ msg: "No se encontró el formulario" });
      }

      // Consulta para obtener la información de los enajenantes
      const enajenantesSQL = `
        SELECT * FROM Enajenante
        WHERE formulario_id = ?
      `;
      const [enajenantesRows] = await connection.query(enajenantesSQL, [
        formulario.id,
      ]);
      const enajenantes = enajenantesRows;

      // Consulta para obtener la información de los adquirentes
      const adquirentesSQL = `
        SELECT * FROM Adquirente
        WHERE formulario_id = ?
      `;
      const [adquirentesRows] = await connection.query(adquirentesSQL, [
        formulario.id,
      ]);
      const adquirentes = adquirentesRows;

      // Construye el JSON de respuesta
      const respuesta = {
        _comment: "",
        CNE: formulario.cne,
        bienRaiz: {
          comuna: formulario.comuna,
          manzana: formulario.manzana,
          predio: formulario.predio,
        },
        enajenantes: enajenantes.map((enajenante) => ({
          RUNRUT: enajenante.runrut,
          porcDerecho: enajenante.porc_derecho,
        })),
        adquirentes: adquirentes.map((adquirente) => ({
          RUNRUT: adquirente.runrut_adq,
          porcDerecho: adquirente.porc_derecho_adq,
        })),
        fojas: formulario.fojas,
        fechaInscripcion: formulario.fecha_inscripcion
          .toISOString()
          .split("T")[0], // Formatea la fecha como 'YYYY-MM-DD'
        nroInscripcion: formulario.numero_inscripcion,
      };

      // Cierra la conexión
      await connection.end();

      // Envía la respuesta
      res.json(respuesta);
    } catch (error) {
      // Maneja el error si ocurre alguno
      console.error("Error en búsqueda:", error);
      res.status(500).json({ msg: "Error en búsqueda" });
    }
  },
  atencion: async (req, res) => {
    try {
      const { numero_atencion } = req.body;

      // Obtiene una nueva conexión
      const connection = await mysql.createConnection({
        host: "flask-g19-miuandes-3b9d.a.aivencloud.com",
        user: "avnadmin",
        password: "AVNS_LHyyUux2JxRT64CsmA5",
        database: "defaultdb",
        port: 18573,
      });
      console.log(numero_atencion);
      // Consulta para obtener el formulario relacionado a la atención
      const formularioSQL = `
        SELECT * FROM Formulario
        WHERE numero_atencion = ?
      `;
      const [formularioRows] = await connection.query(formularioSQL, [
        numero_atencion,
      ]);
      const formulario = formularioRows[0];

      if (!formulario) {
        return res.status(404).json({
          msg: "No se encontró el formulario relacionado a la atención",
        });
      }

      // Consulta para obtener la información de los enajenantes
      const enajenantesSQL = `
        SELECT * FROM Enajenante
        WHERE formulario_id = ?
      `;
      const [enajenantesRows] = await connection.query(enajenantesSQL, [
        formulario.id,
      ]);
      const enajenantes = enajenantesRows;

      // Consulta para obtener la información de los adquirentes
      const adquirentesSQL = `
        SELECT * FROM Adquirente
        WHERE formulario_id = ?
      `;
      const [adquirentesRows] = await connection.query(adquirentesSQL, [
        formulario.id,
      ]);
      const adquirentes = adquirentesRows;

      // Construye el JSON de respuesta
      const respuesta = {
        _comment: "",
        CNE: formulario.cne,
        bienRaiz: {
          comuna: formulario.comuna,
          manzana: formulario.manzana,
          predio: formulario.predio,
        },
        enajenantes: enajenantes.map((enajenante) => ({
          RUNRUT: enajenante.runrut,
          porcDerecho: enajenante.porc_derecho,
        })),
        adquirentes: adquirentes.map((adquirente) => ({
          RUNRUT: adquirente.runrut_adq,
          porcDerecho: adquirente.porc_derecho_adq,
        })),
        fojas: formulario.fojas,
        fechaInscripcion: formulario.fecha_inscripcion
          .toISOString()
          .split("T")[0], // Formatea la fecha como 'YYYY-MM-DD'
        nroInscripcion: formulario.numero_inscripcion,
      };

      // Cierra la conexión
      await connection.end();

      // Envía la respuesta
      res.json(respuesta);
    } catch (error) {
      // Maneja el error si ocurre alguno
      console.error("Error en búsqueda de atención:", error);
      res.status(500).json({ msg: "Error en búsqueda de atención" });
    }
  },
};
module.exports = busquedaController;
