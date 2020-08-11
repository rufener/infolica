<style src="./suiviMandat.css" scoped></style>
<template src="./suiviMandat.html"></template>


<script>
import {handleException} from '@/services/exceptionsHandler';
import {checkPermission} from '@/services/helper';

const moment = require("moment");

export default {
  name: "SuiviMandat",
  props: {},
  data: () => ({
    affaireReadonly: true,
    chefsProjetMO_liste: [],
    confirmDialogActive: false,
    confirmUpdateAffaireDateValidation: false,
    needToCreateSuiviMandat: false,
    operateurs_liste: [],
    showModifiedSuiviMandat: false,
    showNewSuiviMandatBtn: false,
    suiviMandat: {}
  }),

  methods: {
    /*
     * SEARCH AFFAIRE-SUIVI MANDAT
     */
    async searchSuiviMandat() {
      this.searchOperateurs()
      .then(() => {
        this.$http
          .get(
            process.env.VUE_APP_API_URL +
              process.env.VUE_APP_AFFAIRE_SUIVI_MANDAT_ENDPOINT +
              this.$route.params.id,
            {
              withCredentials: true,
              headers: { Accept: "application/json" }
            }
          )
          .then(response => {
            if (response && response.data) {
              this.suiviMandat = response.data;
              if (this.suiviMandat.date !== null) {
                this.suiviMandat.date = moment(this.suiviMandat.date, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
              }
              if (this.suiviMandat.av_33 !== null) {
                this.suiviMandat.av_33 = moment(this.suiviMandat.av_33, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
              }
              if (this.suiviMandat.ap_33 !== null) {
                this.suiviMandat.ap_33 = moment(this.suiviMandat.ap_33, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
              }
              if (this.suiviMandat.av_32 !== null) {
                this.suiviMandat.av_32 = this.chefsProjetMO_liste.filter(x => x.id === this.suiviMandat.av_32).pop();
              }
              if (this.suiviMandat.ap_32 !== null) {
                this.suiviMandat.ap_32 = this.chefsProjetMO_liste.filter(x => x.id === this.suiviMandat.ap_32).pop();
              }
              if (this.suiviMandat.visa !== null) {
                this.suiviMandat.visa = this.chefsProjetMO_liste.filter(x => x.id === this.suiviMandat.visa).pop();
              } 
            }else {
              // Il n'existe pas encore de suivi de mandat pour cette affaire
              this.needToCreateSuiviMandat = true;
            }
          })
          .catch(err => {
            handleException(err, this);
          });
      }
      )
    },

    /**
     * Cherche les opérateurs
     */
    async searchOperateurs() {
      return new Promise((resolve, reject) => {
        this.$http
          .get(
            process.env.VUE_APP_API_URL + process.env.VUE_APP_OPERATEURS_ENDPOINT,
            {
              withCredentials: true,
              headers: { Accept: "application/json" }
            }
          )
          .then(response => {
            if (response.data) {
              this.operateurs_liste = response.data;
              this.chefsProjetMO_liste = response.data
                .filter(x => {
                  return x.responsable;
                })
                .map(x => ({
                  id: x.id,
                  nom: [x.nom, x.prenom].join(" "),
                  toLowerCase: () => [x.nom, x.prenom].join(" ").toLowerCase(),
                  toString: () => [x.nom, x.prenom].join(" ")
                }));
              resolve(response);
            }
          })
          .catch(err => reject(err));
      })
    },

    /**
     * Création d'un nouveau suivi
     */
    newSuiviMandat() {
      var formData = new FormData();
      formData.append("affaire_id", this.$route.params.id);

      this.$http
        .post(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_SUIVI_MANDAT_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response) {
            this.searchSuiviMandat();
            this.needToCreateSuiviMandat = false;
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    onCancelEditSuiviMandat() {
      this.searchSuiviMandat();
    },

    onConfirmEditSuiviMandat() {
      var formData = new FormData();
      if (this.suiviMandat.id) {
        formData.append("id", this.suiviMandat.id);
      }
      if (this.suiviMandat.affaire_id) {
        formData.append("affaire_id", this.suiviMandat.affaire_id);
      }
      if (this.suiviMandat.av_11) {
        formData.append("av_11", this.suiviMandat.av_11);
      }
      if (this.suiviMandat.av_12) {
        formData.append("av_12", this.suiviMandat.av_12);
      }
      if (this.suiviMandat.av_21) {
        formData.append("av_21", this.suiviMandat.av_21);
      }
      if (this.suiviMandat.av_31) {
        formData.append("av_31", this.suiviMandat.av_31);
      }
      if (this.suiviMandat.av_32 && this.suiviMandat.av_32.id) {
        formData.append("av_32", this.suiviMandat.av_32.id);
      }
      if (this.suiviMandat.av_33) {
        formData.append("av_33", moment(this.suiviMandat.av_33, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));
      }
      if (this.suiviMandat.av_41) {
        formData.append("av_41", this.suiviMandat.av_41);
      }
      if (this.suiviMandat.av_51) {
        formData.append("av_51", this.suiviMandat.av_51);
      }
      if (this.suiviMandat.pdt_11) {
        formData.append("pdt_11", this.suiviMandat.pdt_11);
      }
      if (this.suiviMandat.pdt_12) {
        formData.append("pdt_12", this.suiviMandat.pdt_12);
      }
      if (this.suiviMandat.pdt_21) {
        formData.append("pdt_21", this.suiviMandat.pdt_21);
      }
      if (this.suiviMandat.pdt_22) {
        formData.append("pdt_22", this.suiviMandat.pdt_22);
      }
      if (this.suiviMandat.pdt_31) {
        formData.append("pdt_31", this.suiviMandat.pdt_31);
      }
      if (this.suiviMandat.pdt_41) {
        formData.append("pdt_41", this.suiviMandat.pdt_41);
      }
      if (this.suiviMandat.pdt_42) {
        formData.append("pdt_42", this.suiviMandat.pdt_42);
      }
      if (this.suiviMandat.ap_11) {
        formData.append("ap_11", this.suiviMandat.ap_11);
      }
      if (this.suiviMandat.ap_12) {
        formData.append("ap_12", this.suiviMandat.ap_12);
      }
      if (this.suiviMandat.ap_21) {
        formData.append("ap_21", this.suiviMandat.ap_21);
      }
      if (this.suiviMandat.ap_22) {
        formData.append("ap_22", this.suiviMandat.ap_22);
      }
      if (this.suiviMandat.ap_31) {
        formData.append("ap_31", this.suiviMandat.ap_31);
      }
      if (this.suiviMandat.ap_32 && this.suiviMandat.ap_32.id) {
        formData.append("ap_32", this.suiviMandat.ap_32.id);
      }
      if (this.suiviMandat.ap_33) {
        formData.append("ap_33", moment(this.suiviMandat.ap_33, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));
      }
      if (this.suiviMandat.ap_41) {
        formData.append("ap_41", this.suiviMandat.ap_41);
      }
      if (this.suiviMandat.ap_42) {
        formData.append("ap_42", this.suiviMandat.ap_42);
      }
      if (this.suiviMandat.visa && this.suiviMandat.visa !== "") {
        formData.append("visa", this.suiviMandat.visa.id);
      } else {
        formData.append("visa", null);
      }
      if (this.suiviMandat.date) {
        formData.append("date",
          moment(this.suiviMandat.date, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));
      } else {
        formData.append("date", null);
      }

      this.$http
        .put(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_SUIVI_MANDAT_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response) {
            this.$root.$emit("ShowMessage", "Le suivi du mandat a été mis à jour avec succès");
            this.searchSuiviMandat();
            if (this.suiviMandat.date !== null) {
              this.confirmDialogActive = true;
            }
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Update affaire date validation
     */
    updateAffaireDateValidation(){
      let formData = new FormData();
      formData.append("id_affaire", this.$route.params.id);
      formData.append("date_validation", moment(this.suiviMandat.date, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));

      this.$http.put(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRES_ENDPOINT,
        formData,
        {
          withCredentials: true,
          headers: {Accept: "application/json"}
        }
      ).then(() => this.$parent.setAffaire())
      .catch(err => handleException(err, this));
    },

  },

  mounted: function() {
    this.searchSuiviMandat();
    this.searchOperateurs();

    this.affaireReadonly = !checkPermission(process.env.VUE_APP_AFFAIRE_SUIVI_EDITION) || this.$parent.parentAffaireReadOnly;
  }
};
</script>



