const mysql = require("mysql2/promise");
const pool = require("../database");
const lookupDBController = require("./lookupDB.controller");
const insertDBController = require("./insertDB.controller");

const SERVER_ERROR_STATUS = 500;

const isValidDate = (dateString) => {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  return regex.test(dateString) && !isNaN(Date.parse(dateString));
};

const getNumeroAtencion = async () => {
  try {

    const rows = await lookupDBController.FormularioUltimoNumneroAtencion();

    if (rows.length > 0) {
      
      const lastNumeroAtencion = Number(rows[0].numero_atencion);
      return isNaN(lastNumeroAtencion) ? 1 : lastNumeroAtencion + 1;

    } 
    else {     
      return 1;
    }
  } catch (error) {
    console.error(`Failed to get "numero_atencion": ${error}`);
    throw error;
  }
};

const formularioController = {
  createFormulario: async (req, res) => {
    let connection;
    try {

      const formularios = req.body["F2890"];
      const connection = await pool.getConnection();
      await connection.beginTransaction();

      const numeroAtencion = await getNumeroAtencion();

      await Promise.all(
        formularios.map(async (formulario) => {
          try {
            if (!formulario.bienRaiz) {
              throw new Error("bienRaiz is not defined in the form");
            }

            const {
              _comment,
              CNE,
              bienRaiz,
              enajenantes = [],
              adquirentes = [],
              fojas,
              fechaInscripcion,
              nroInscripcion,
            } = formulario;

            const { comuna, manzana, predio } = bienRaiz;

            if (!isValidDate(fechaInscripcion)) {
              throw new Error("Fecha de inscripción inválida");
            }

            const transactionData = await insertDBController.Formulario(numeroAtencion, CNE, comuna, manzana, predio, fojas, fechaInscripcion, nroInscripcion);
            const formularioId = transactionData.insertId;

            await Promise.all(
              enajenantes.map(async (enajenante) => {
                await insertDBController.Enajenante(enajenante.RUNRUT, enajenante.porcDerecho, formularioId);
              })
            );

            await Promise.all(
              adquirentes.map(async (adquirente) => {
                await insertDBController.Adquiriente(adquirente.RUNRUT, adquirente.porcDerecho, formularioId)
              })
            );
          } 
          catch (error) {
            console.error("Error processing formulario:", error);
          }
        })
      );

      await connection.commit();

      res.json({ msg: "Formularios creados exitosamente" });

      
    } 
    catch (error) {
      if (connection) {
        await connection.rollback();
      }
      res.status(SERVER_ERROR_STATUS).json({ msg: error.message });
    } 
    finally {
      if (connection) {
        connection.release();
      }
    }
  },
};

module.exports = formularioController;
