<style src="./quittancePCOP.css" scoped></style>
<template src="./quittancePCOP.html"></template>


<script>
import { handleException } from "@/services/exceptionsHandler";
import {
  getCurrentDate,
  getCadastres,
  stringifyAutocomplete,
  getDocument,
  setClientsAdresse_
} from "@/services/helper";
import moment from "moment";

export default {
  name: "quittancePCOP",
  props: {
    affaire: { type: Object },
    affaire_numeros_anciens: { type: Array },
    affaire_numeros_nouveaux: { type: Array }
  },
  components: {},
  data: () => ({
    form: {
      adresse_: null,
      entreprise: null,
      titre: null,
      nref: null,
      vref: null,
      dateEnvoi: null,
      dateDemande: null,
      numerosReserves: null,
      nombreNumerosReserves: null,
      bfBase: null,
      cadastre: null
    },
    showQuittancePCOPDialog: false,
    cadastres_liste: [],
    numeros_pcop: [],
    numeros_base: []
  }),

  methods: {
    /**
     * Ouvrir le dialog
     */
    openQuittancePCOPDialog() {
      this.showQuittancePCOPDialog = true;
      this.getNumerosReservesPCOP();
    },

    /**
     * get cadastres
     */
    initCadastresListe() {
      getCadastres()
        .then(
          response =>
            (this.cadastres_liste = stringifyAutocomplete(response.data))
        )
        .catch(err => handleException(err, this));
    },

    /***
     * Get client from affaire.client_commande_id
     */
    async getClientAffaire() {
      return new Promise((resolve, reject) => {
        this.$http.get(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_CLIENTS_ENDPOINT +
          "/" + this.affaire.client_commande_id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        ).then(response => resolve(response))
        .catch(err => reject(err));
      })
    },

    /**
     * Récupère les nouveaux numéros de type PCOP
     */
    getNumerosReservesPCOP() {
      this.numeros_pcop = this.affaire_numeros_nouveaux.filter(x => x.numero_type_id===Number(process.env.VUE_APP_NUMERO_TYPE_PCOP) && x.active);
      this.numeros_base = [];
      let tmp = [];
      // Get set of unique BF base
      this.affaire_numeros_nouveaux.map(x => {
        if (!tmp.includes(x.numero_base_id) && x.numero_base_id !== null && x.active){
          tmp.push(x.numero_base_id);
          this.numeros_base.push({numero_base: x.numero_base, numero_base_id: x.numero_base_id});
        }
      });
    },

    /**
     * Update les numéros de et à en fonction du BF de base
     */
    updateNumerosPCOP() {
      const tmp = [];
      this.affaire_numeros_nouveaux.filter(x => x.numero_base === this.form.bfBase).map(x => {
        if (x.active) {
          tmp.push(x.numero)}
        });
      this.form.numeros_de = Math.min(...tmp);
      this.form.numeros_a = Math.max(...tmp);
    },


    /**
     * Initialiser le formulaire Dialog
     */
    initForm() {
      this.getClientAffaire()
      .then(response => {
        if (response && response.data) {
          let client = setClientsAdresse_(response.data, "\n");
          this.form.adresse_ = client.adresse_;
          this.form.titre = client.titre;
        }
      }).catch(err => handleException(err));

      this.form = {
        nref: this.affaire.id,
        vref: this.affaire.vref,
        cadastre: this.affaire.cadastre,
        dateEnvoi: getCurrentDate(),
        dateDemande: moment(this.affaire.date_ouverture, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT),
        numeros_de: "",
        numeros_a: "",
        nombreNumerosReserves: "",
        bfBase: ""
      };
    },

    /**
     * Créer la quittance de création de parts de copropriétés
     */
    callCreateQuittancePCOP() {
      let formData = new FormData();

      formData.append("template", "ParCop");
      formData.append(
        "values",
        JSON.stringify({
          ADRESSE_: this.form.adresse_,
          TITRE: this.form.titre,
          NREF: this.form.nref,
          VREF: String(this.form.vref),
          DATEENVOI: String(this.form.dateEnvoi),
          DATEDEMANDE: String(this.form.dateDemande),
          NUMEROSRESERVES: String(this.form.numeros_de) + " à " + String(this.form.numeros_a),
          NOMBRENUMEROS: String(Number(this.form.numeros_a)-Number(this.form.numeros_de)+1),
          BIENFONDSBASE: String(this.form.bfBase),
          CADASTRE: this.form.cadastre
        })
      );

      getDocument(formData)
      .then(response => {
          this.$root.$emit("ShowMessage", "Le fichier '" + response + " se trouve dans le dossier 'Téléchargement'")
          this.showQuittancePCOPDialog = false;
      })
      .catch(err => handleException(err, this));
    }

  },
  mounted: function() {
    this.initForm();
    this.initCadastresListe();
  }
};
</script>



