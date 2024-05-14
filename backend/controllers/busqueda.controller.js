const mysql = require("mysql2/promise");
const pool = require("../database");
const lookupDBController = require("./lookupDB.controller")

const NOT_FOUND_STATUS = 404;
const SERVER_ERROR_STATUS = 500;

const busquedaController = {
  
  respuestaFormulario: async (formulario) => {
    
    const { id, cne, comuna, manzana, predio, fojas, fecha_inscripcion, numero_inscripcion } = formulario;
    const enajenantes = await lookupDBController.EnajenanteID(formulario.id);
    const adquirentes = await lookupDBController.AdquirienteID(formulario.id);

    return {
      _comment: "",
      CNE: cne,
      bienRaiz: {
        comuna: comuna,
        manzana: manzana,
        predio: predio,
      },
      enajenantes: enajenantes.map(({ runrut, porc_derecho }) => ({
        RUNRUT: runrut,
        porcDerecho: porc_derecho,
      })),
      adquirentes: adquirentes.map(({ runrut_adq, porc_derecho_adq }) => ({
        RUNRUT: runrut_adq,
        porcDerecho: porc_derecho_adq,
      })),
      fojas: fojas,
      fechaInscripcion: fecha_inscripcion.toISOString().split("T")[0], // Formatea la fecha como 'YYYY-MM-DD'
      nroInscripcion: numero_inscripcion,
    };
  },

  respuestaMultipropietario: async (multipropietario) => {
    const { id, comuna, manzana, predio, run, derecho, fojas, fecha_inscripcion, ano_inscripccion, 
      numero_inscripcion, ano_vigencia_i, ano_vigencia_f } = multipropietario;

    return {
      _comment: "",
      bienRaiz: {
        comuna: comuna,
        manzana: manzana,
        predio: predio,
      },
      propietario: {
        RUNRUT: run,
        derecho: derecho,
      },
      fojas: fojas,
      fechaInscripcion: fecha_inscripcion.toISOString().split("T")[0], // Formatea la fecha como 'YYYY-MM-DD'
      nroInscripcion: numero_inscripcion,
      anoInscripcion: ano_inscripccion,
      vigencia: {
        inicio: ano_vigencia_i,
        fin: ano_vigencia_f,
      }
    };
  },
  
  formularioCMP: async (req, res) => {
    try {

      const { comuna, manzana, predio } = req.body;
      const formularios = await lookupDBController.FormularioCMP(comuna, manzana, predio);

      if (!formularios || formularios.length === 0) {
        return res.status(NOT_FOUND_STATUS).json({ msg: "No se encontró el formulario" });
      }
      
      const respuestas = await Promise.all(
        formularios.map(async (formulario) => {
          return await this.respuestaFormulario(formulario);
        })
      );

      await connection.release();

      res.json(respuestas);

    } catch (error) {

      console.error("Error en búsqueda:", error);
      res.status(SERVER_ERROR_STATUS).json({ msg: "Error en búsqueda" });

    }
  },

  multipropietarioCMP: async (req, res) => {
    try {

      const { comuna, manzana, predio } = req.body;
      const multipropietarios = await lookupDBController.MultipropietarioCMP(comuna, manzana, predio);

      if (!multipropietarios || multipropietarios.length === 0) {
        return res.status(NOT_FOUND_STATUS).json({ msg: "No se encontró el multipropietario" });
      }
      
      const respuestas = await Promise.all(
        multipropietarios.map(async (multipropietario) => {
          return await this.respuestaMultipropietario(multipropietario);
        })
      );

      await connection.release();

      res.json(respuestas);

    } catch (error) {

      console.error("Error en búsqueda:", error);
      res.status(SERVER_ERROR_STATUS).json({ msg: "Error en búsqueda" });

    }
  },

  formularioYear: async (req, res) => {
    try {
      
      const { year } = req.body
      const formularios = await lookupDBController.FormularioYear(year);

      if (!formularios || formularios.length === 0) {
        return res.status(NOT_FOUND_STATUS).json({ msg: "No se encontró el formulario" });
      }

      const respuestas = await Promise.all(
        formularios.map(async (formulario) => {
          return await this.respuestaFormulario(formulario);
        })
      );

      await connection.release();

      res.json(respuestas);

    } catch (error) {
      
      console.error("Error en búsqueda:", error);
      res.status(SERVER_ERROR_STATUS).json({ msg: "Error en búsqueda" });

    }
  },

  multipropietarioYear: async (req, res) => {
    try {
      
      const { year } = req.body
      const multipropietarios = await lookupDBController.MultipropietarioYear(year);

      if (!multipropietarios || multipropietarios.length === 0) {
        return res.status(NOT_FOUND_STATUS).json({ msg: "No se encontró el multipropietario" });
      }

      const respuestas = await Promise.all(
        multipropietarios.map(async (multipropietario) => {
          return await this.respuestaMultipropietario(multipropietario);
        })
      );

      await connection.release();

      res.json(respuestas);

    } catch (error) {
      
      console.error("Error en búsqueda:", error);
      res.status(SERVER_ERROR_STATUS).json({ msg: "Error en búsqueda" });

    }
  },
  
  formularioAtencion: async (req, res) => {
    try {
      
      const { numero_atencion } = req.body;
      const formularios = await lookupDBController.FormularioAtencion(numero_atencion);

      if (!formularios || formularios.length === 0) {
        return res.status(NOT_FOUND_STATUS).json({
          msg: "No se encontró el formulario relacionado a la atención",
        });
      }

      const respuestas = await Promise.all(
        formularios.map(async (formulario) => {
          return await this.respuestaFormulario(formulario);
        })
      );

      await connection.release();

      res.json(respuestas);

    } catch (error) {
      
      console.error("Error en búsqueda de atención:", error);
      res.status(SERVER_ERROR_STATUS).json({ msg: "Error en búsqueda de atención" });

    }
  },
};

module.exports = busquedaController;