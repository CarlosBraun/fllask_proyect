const mysql = require("mysql2/promise");
const pool = require("../database");
const lookupDBController = require("./lookupDB.controller");
const insertDBController = require("./insertDB.controller");

// Función para verificar si una cadena es una fecha válida en el formato 'YYYY-MM-DD'
const isValidDate = (dateString) => {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  return regex.test(dateString) && !isNaN(Date.parse(dateString));
};

const multipropietarioController = {
  createMultipropietario: async (req, res) => {
    let connection;
    try {
      
      const { comuna, manzana, predio } = req.body;
      const formularios = await lookupDBController.FormularioCMP(comuna, manzana, predio);

      for (let formulario of formularios) {
        const multipropietarioData = {
          comuna: formulario.comuna,
          manzana: formulario.manzana,
          predio: formulario.predio,
          run: formulario.runrut, 
          derecho: formulario.porc_derecho,
          fojas: formulario.fojas,
          fecha_inscripcion: formulario.fecha_inscripcion,
          ano_inscripccion: new Date(formulario.fecha_inscripcion).getFullYear(),
          numero_inscripcion: formulario.numero_inscripcion,
          ano_vigencia_i: formulario.fecha_inscripcion,
          ano_vigencia_f: null
        };

        await insertDBController.Multipropietrio(formulario.comuna, formulario.manzana, formulario.predio, formulario.runrut, formulario.porc_derecho, formulario.fojas, 
                                                 formulario.fecha_inscripcion, new Date(formulario.fecha_inscripcion).getFullYear(), formulario.numero_inscripcion, 
                                                 formulario.fecha_inscripcion, null);
      }

      res.status(200).send({ message: 'Multipropietario entries created successfully.' });
      
      
    } catch (error) {
      if (connection) {
        await connection.rollback();
      }
      res.status(500).json({ msg: error.message });
    } finally {
      if (connection) {
        connection.release();
      }
    }
  },
};

module.exports = multipropietarioController;
