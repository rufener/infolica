<style src="./controlePPE.css" scoped></style>
<template src="./controlePPE.html"></template>


<script>
import {handleException} from '@/services/exceptionsHandler';
import {checkPermission} from '@/services/helper';

const moment = require('moment')

export default {
  name: "ControlePPE",
  props: {},
  data: () => ({
    showNewControlePPEBtn: false,
    affaireReadonly: true,
    needToCreateControlePPE: false,
    chefsProjetMO_liste: [],
    showCreatedControlePPE: false,
    controlePPE: {}
  }),

  methods: {
    /*
     * SEARCH AFFAIRE-ControlePPE
     */
    async searchControlePPE() {
      await this.searchOperateurs();
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_AFFAIRE_CONTROLE_PPE_ENDPOINT +
          this.$route.params.id,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response => {
          if (response && response.data) {
            this.controlePPE = response.data;
            if (this.controlePPE.visa) {
              this.controlePPE.visa = this.chefsProjetMO_liste.filter(x => {
              return x.id == this.controlePPE.visa
              })[0];
            }
            if (this.controlePPE.date) {
              this.controlePPE.date = moment(this.controlePPE.date, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
              }
          } else {
            // Il n'existe pas encore de suivi de mandat pour cette affaire
            this.needToCreateControlePPE = true;
          }
        })
        .catch(err => {
          handleException(err, this);
        });
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
              headers: {"Accept": "application/json"}
            }
          )
          .then(response => {
            if (response.data) {
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
                resolve(this.chefsProjetMO_liste);
            }
          })
          .catch(() => reject);
      })
    },

    /**
     * Création d'un nouveau suivi
     */
    newControlePPE() {
      var formData = new FormData();
      formData.append("affaire_id", this.$route.params.id);

      this.$http
        .post(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_CONTROLE_PPE_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response => {
          if (response) {
            this.$root.$emit("ShowMessage", "Le formulaire de contrôle a été créé avec succès")
            this.searchControlePPE();
            this.needToCreateControlePPE = false;
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    onCancelEditControlePPE() {
      this.searchControlePPE();
    },

    onConfirmEditControlePPE() {
      var formData = new FormData();
      formData.append("id", this.controlePPE.id);
      formData.append("affaire_id", this.controlePPE.affaire_id);
      if (this.controlePPE.doss_proj_1) {
        formData.append("doss_proj_1", this.controlePPE.doss_proj_1);
      }
      if (this.controlePPE.doss_proj_2) {
        formData.append("doss_proj_2", this.controlePPE.doss_proj_2);
      }
      if (this.controlePPE.psit_1) {
        formData.append("psit_1", this.controlePPE.psit_1);
      }
      if (this.controlePPE.psit_2) {
        formData.append("psit_2", this.controlePPE.psit_2);
      }
      if (this.controlePPE.psit_3) {
        formData.append("psit_3", this.controlePPE.psit_3);
      }
      if (this.controlePPE.psit_4) {
        formData.append("psit_4", this.controlePPE.psit_4);
      }
      if (this.controlePPE.psit_5) {
        formData.append("psit_5", this.controlePPE.psit_5);
      }
      if (this.controlePPE.psit_6) {
        formData.append("psit_6", this.controlePPE.psit_6);
      }
      if (this.controlePPE.psit_7) {
        formData.append("psit_7", this.controlePPE.psit_7);
      }
      if (this.controlePPE.pamext_1) {
        formData.append("pamext_1", this.controlePPE.pamext_1);
      }
      if (this.controlePPE.pet_1) {
        formData.append("pet_1", this.controlePPE.pet_1);
      }
      if (this.controlePPE.pet_2) {
        formData.append("pet_2", this.controlePPE.pet_2);
      }
      if (this.controlePPE.pet_3) {
        formData.append("pet_3", this.controlePPE.pet_3);
      }
      if (this.controlePPE.pet_4) {
        formData.append("pet_4", this.controlePPE.pet_4);
      }
      if (this.controlePPE.pet_5) {
        formData.append("pet_5", this.controlePPE.pet_5);
      }
      if (this.controlePPE.pet_6) {
        formData.append("pet_6", this.controlePPE.pet_6);
      }
      if (this.controlePPE.pet_7) {
        formData.append("pet_7", this.controlePPE.pet_7);
      }
      if (this.controlePPE.pet_8) {
        formData.append("pet_8", this.controlePPE.pet_8);
      }
      if (this.controlePPE.pet_9) {
        formData.append("pet_9", this.controlePPE.pet_9);
      }
      if (this.controlePPE.pet_10) {
        formData.append("pet_10", this.controlePPE.pet_10);
      }
      if (this.controlePPE.pet_11) {
        formData.append("pet_11", this.controlePPE.pet_11);
      }
      if (this.controlePPE.pet_12) {
        formData.append("pet_12", this.controlePPE.pet_12);
      }
      if (this.controlePPE.pet_13) {
        formData.append("pet_13", this.controlePPE.pet_13);
      }
      if (this.controlePPE.pet_14) {
        formData.append("pet_14", this.controlePPE.pet_14);
      }
      if (this.controlePPE.pet_15) {
        formData.append("pet_15", this.controlePPE.pet_15);
      }
      if (this.controlePPE.pet_16) {
        formData.append("pet_16", this.controlePPE.pet_16);
      }
      if (this.controlePPE.pet_17) {
        formData.append("pet_17", this.controlePPE.pet_17);
      }
      if (this.controlePPE.pet_18) {
        formData.append("pet_18", this.controlePPE.pet_18);
      }
      if (this.controlePPE.pet_19) {
        formData.append("pet_19", this.controlePPE.pet_19);
      }
      if (this.controlePPE.pet_20) {
        formData.append("pet_20", this.controlePPE.pet_20);
      }
      if (this.controlePPE.pet_21) {
        formData.append("pet_21", this.controlePPE.pet_21);
      }
      if (this.controlePPE.pco_1) {
        formData.append("pco_1", this.controlePPE.pco_1);
      }
      if (this.controlePPE.pco_2) {
        formData.append("pco_2", this.controlePPE.pco_2);
      }
      if (this.controlePPE.pco_3) {
        formData.append("pco_3", this.controlePPE.pco_3);
      }
      if (this.controlePPE.pco_4) {
        formData.append("pco_4", this.controlePPE.pco_4);
      }
      if (this.controlePPE.pco_5) {
        formData.append("pco_5", this.controlePPE.pco_5);
      }
      if (this.controlePPE.pco_6) {
        formData.append("pco_6", this.controlePPE.pco_6);
      }
      if (this.controlePPE.pco_7) {
        formData.append("pco_7", this.controlePPE.pco_7);
      }
      if (this.controlePPE.facade_1) {
        formData.append("facade_1", this.controlePPE.facade_1);
      }
      if (this.controlePPE.facade_2) {
        formData.append("facade_2", this.controlePPE.facade_2);
      }
      if (this.controlePPE.facade_3) {
        formData.append("facade_3", this.controlePPE.facade_3);
      }
      if (this.controlePPE.facade_4) {
        formData.append("facade_4", this.controlePPE.facade_4);
      }
      if (this.controlePPE.form_leg_1) {
        formData.append("form_leg_1", this.controlePPE.form_leg_1);
      }
      if (this.controlePPE.form_leg_2) {
        formData.append("form_leg_2", this.controlePPE.form_leg_2);
      }
      if (this.controlePPE.form_leg_3) {
        formData.append("form_leg_3", this.controlePPE.form_leg_3);
      }
      if (this.controlePPE.form_leg_4) {
        formData.append("form_leg_4", this.controlePPE.form_leg_4);
      }
      if (this.controlePPE.form_leg_5) {
        formData.append("form_leg_5", this.controlePPE.form_leg_5);
      }
      if (this.controlePPE.form_leg_6) {
        formData.append("form_leg_6", this.controlePPE.form_leg_6);
      }
      if (this.controlePPE.form_leg_7) {
        formData.append("form_leg_7", this.controlePPE.form_leg_7);
      }
      if (this.controlePPE.form_leg_8) {
        formData.append("form_leg_8", this.controlePPE.form_leg_8);
      }
      if (this.controlePPE.form_leg_9) {
        formData.append("form_leg_9", this.controlePPE.form_leg_9);
      }
      if (this.controlePPE.fact_1) {
        formData.append("fact_1", this.controlePPE.fact_1);
      }
      if (this.controlePPE.fact_2) {
        formData.append("fact_2", this.controlePPE.fact_2);
      }
      if (this.controlePPE.fact_3) {
        formData.append("fact_3", this.controlePPE.fact_3);
      }
      if (this.controlePPE.fact_4) {
        formData.append("fact_4", this.controlePPE.fact_4);
      }
      if (this.controlePPE.fact_5) {
        formData.append("fact_5", this.controlePPE.fact_5);
      }
      if (this.controlePPE.fact_6) {
        formData.append("fact_6", this.controlePPE.fact_6);
      }
      if (this.controlePPE.fact_7) {
        formData.append("fact_7", this.controlePPE.fact_7);
      }
      if (this.controlePPE.visa) {
        formData.append("visa", this.controlePPE.visa.id);
      }
      if (this.controlePPE.date) {
        formData.append("date", moment(this.controlePPE.date, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));
      }

      this.$http
        .put(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_CONTROLE_PPE_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response => {
          if (response) {
            this.$root.$emit("ShowMessage", "Le formulaire de contrôle a été mis à jour avec succès")
            this.searchControlePPE();
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },
  },

  mounted: function() {
    this.searchControlePPE();
    this.searchOperateurs();

    this.affaireReadonly = !checkPermission(process.env.VUE_APP_AFFAIRE_CONTROLE_EDITION) || this.$parent.parentAffaireReadOnly;
  }
};
</script>



