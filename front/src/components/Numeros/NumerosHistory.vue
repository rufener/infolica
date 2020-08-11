<style src="./numerosHistory.css" scoped></style>
<template src="./numerosHistory.html"></template>


<script>
import { checkPermission, getCadastres, getEtatsNumeros, stringifyAutocomplete } from "@/services/helper";
import {handleException} from '@/services/exceptionsHandler'
import moment from "moment";

export default {
  name: "NumerosHistory",
  props: {},
  data: () => ({
    cadastre_liste: [],
    numero: [],
    numero_edit: [],
    numero_affaires: [],
    numero_provenance: [],
    numero_destination: [],
    editNumeroAllowed: false,
    editionActivated: false,
    etatsNumeros: [],
  }),

  methods: {
    /**
     * Initialize permissions to edit numero
     */
    initPermissions() {
      this.editNumeroAllowed = checkPermission(process.env.VUE_APP_AFFAIRE_NUMERO_EDITION)
    },

    /*
     * Get Numero_by_id
     */
    async getNumeroById() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_NUMEROS_ENDPOINT +
          this.$route.params.id,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        ).then(response => {
          if (response && response.data) {
            this.numero = response.data;
            this.numero.diff = "Non";
            if (this.numero.diff_entree && !this.numero.diff_sortie) {
              this.numero.diff = "Oui";
            }
            if (!this.numero.suffixe) {
              this.numero.suffixe = "-"
            }
          }
        }).catch(err => {
          handleException(err, this);
        });
    },


    /*
     * Init Cadastres list
     */
    initCadastresList() {
      getCadastres()
      .then(response => {
        if (response && response.data) {
          this.cadastre_liste = response.data.map(function(obj) {
            return obj.nom;
          });
        }
      }).catch(err => {
        handleException(err, this);
      });
    },


    /*
     * Get affaires par numéro
     */
    async getNumeroAffaires() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_NUMERO_AFFAIRES_ENDPOINT +
          this.$route.params.id,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            }
        ).then(response => {
          if (response && response.data) {
            this.numero_affaires = response.data;
          }
        }).catch(err => {
          handleException(err, this);
        })
    },


    /*
     * Get Numero_provenance
     */
    async getNumeroProvenance() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_NUMERO_RELATIONS_BASE_ENDPOINT +
          this.$route.params.id,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        ).then(response => {
          if (response.data) {
            this.numero_provenance = response.data.map(x => x.numero_base + x.numero_base_suffixe);
          } else {
            this.numero_provenance = "-"
          }
        }).catch(err => {
          handleException(err, this);
        });
    },


    /*
     * Get Numero_destination
     */
    async getNumeroDestination() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_NUMERO_RELATIONS_ASSOCIE_ENDPOINT +
          this.$route.params.id,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        ).then(response => {
          if (response.data) {
            this.numero_destination = response.data.map(x => x.numero_associe + x.numero_associe_suffixe);
          } else {
            this.numero_destination = "-"
          }
        }).catch(err => {
          handleException(err, this);
        });
    },

    /*
     * Open numéro in new tab
     */
    doOpenAffaire(id) {
      this.$router.push({ name: "AffairesDashboard", params: {id}});
    },

    /**
     * Ouvrir le md-dialog pour éditer un numéro
     */
    openEditionNumero() {
      getEtatsNumeros()
      .then(response => this.etatsNumeros = stringifyAutocomplete(response.data))
      .catch(err => handleException(err, this))

      this.numero_edit = Object.assign({} ,this.numero);
      if (this.numero_edit.diff_entree) {
        this.numero_edit.diff_entree = moment(this.numero_edit.diff_entree, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT)
      }
      if (this.numero_edit.diff_sortie) {
        this.numero_edit.diff_sortie = moment(this.numero_edit.diff_entree, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT)
      }
      this.editionActivated = true;
    },

    /**
     * on select Etat Numero séparer id et nom
     */
    onSelectEtatNumero(obj) {
      this.numero_edit.etat_id = obj.id;
      this.numero_edit.etat = obj.nom
    },

    /**
     * Enregistrer les modifications
     */
    onConfirmEditNumero() {
      this.editionActivated = false;

      let _num = this.numero_edit;
      var promises = [];
      if (this.numero_edit.etat_id !== this.numero.etat_id) {
        promises.push(this.saveNumeroEtat(_num));
        promises.push(this.saveNumeroEtatHisto(_num));
      }
      if (moment(this.numero_edit.diff_entree, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS) 
              !== moment(this.numero.diff_entree).format(process.env.VUE_APP_DATEFORMAT_WS) ||
          moment(this.numero_edit.diff_sortie, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS) 
              !== moment(this.numero.diff_sortie).format(process.env.VUE_APP_DATEFORMAT_WS)) {

        promises.push(this.saveNumeroMatDiff(_num));
      }

      Promise.all(promises)
      .then(() => {
        this.$root.$emit("ShowMessage", "Les modifications ont été effectuées avec succès");
        this.getNumeroById();
      })
      .catch(err => handleException(err, this));
    },

    /**
     * Save numero
     */
    saveNumeroEtat(num) {
      var formData = new FormData();
      formData.append("id", num.id);
      formData.append("etat_id", num.etat_id);
      
      return new Promise((resolve, reject) => {
        this.$http.put(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_NUMEROS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then((response) => resolve(response))
        .catch(err => reject(err))
      });
    },

    /**
     * Save numero etat histo
     */
    saveNumeroEtatHisto(num) {
      var formData = new FormData();
      formData.append("numero_id", num.id);
      formData.append("numero_etat_id", num.etat_id);
      formData.append("date", moment(new Date()).format("YYYY-MM-DD"));

      return new Promise((resolve, reject) => {
        this.$http.post(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_NUMEROS_ETAT_HISTO_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then((response) => resolve(response))
        .catch(err => reject(err))
      });
    },


    /**
     * Enregistrer la mat-diff
     */
    saveNumeroMatDiff(num) {
      var formData = new FormData();
      formData.append("numero_id", num.id);
      formData.append("date_entree", moment(num.diff_entree, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));
      
      if (num.diff_id) {
        formData.append("id", num.diff_id);
      }
      
      // Si une date est donnée, la stocker, sinon la supprimer
      num.diff_sortie !== null ? 
        formData.append("date_sortie", moment(num.diff_sortie, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS)):
        formData.append("date_sortie", null)

      return new Promise((resolve, reject) => {
        var req
        if (num.diff_id) {
          req = this.$http.put(
            process.env.VUE_APP_API_URL +
            process.env.VUE_APP_NUMEROS_DIFFERES_ENDPOINT,
            formData,
            {
              withCredentials: true,
              headers: {Accept: "application/json"}
            }
          )
        } else {
          req = this.$http.post(
            process.env.VUE_APP_API_URL +
            process.env.VUE_APP_NUMEROS_DIFFERES_ENDPOINT,
            formData,
            {
              withCredentials: true,
              headers: {Accept: "application/json"}
            }
          )
        }
        req.then(response => resolve(response))
        .catch(err => reject(err))
      });
    },

  },

  mounted: function() {
    this.getNumeroById();
    this.initCadastresList();
    this.getNumeroAffaires();
    this.getNumeroProvenance();
    this.getNumeroDestination();
    this.initPermissions();
  }
};
</script>

