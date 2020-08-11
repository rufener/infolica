<style src="./controleMutation.css" scoped></style>
<template src="./controleMutation.html"></template>


<script>
import {handleException} from '@/services/exceptionsHandler';
import {checkPermission} from '@/services/helper';

const moment = require('moment')

export default {
  name: "ControleMutation",
  props: {},
  data: () => ({
    affaireReadonly: true,
    showNewControleMutationBtn: false,
    needToCreateControleMutation: false,
    chefsProjetMO_liste: [],
    controleMutation: {}
  }),

  methods: {
    /*
     * SEARCH AFFAIRE-ControleMutation
     */
    async searchControleMutation() {
      await this.searchOperateurs();
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_AFFAIRE_CONTROLE_MUTATION_ENDPOINT +
          this.$route.params.id,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response => {
          if (response && response.data) {
            this.controleMutation = response.data;
            // Lier l'id du visa à son nom
            if (this.controleMutation.visa) {
              this.controleMutation.visa = this.chefsProjetMO_liste.filter(x => {
              return x.id == this.controleMutation.visa
              })[0];
            }
            if (this.controleMutation.date) {
              this.controleMutation.date = moment(this.controleMutation.date, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
            }
          } else {
            // Il n'existe pas encore de suivi de mandat pour cette affaire
            this.needToCreateControleMutation = true;
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
    newControleMutation() {
      var formData = new FormData();
      formData.append("affaire_id", this.$route.params.id);

      this.$http
        .post(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_CONTROLE_MUTATION_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response => {
          if (response) {
            this.$root.$emit("ShowMessage", "Le formulaire de contrôle a été créé avec succès")
            this.searchControleMutation();
            this.needToCreateControleMutation = false;
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    onCancelEditControleMutation() {
      this.searchControleMutation();
    },

    onConfirmEditControleMutation() {
      var formData = new FormData();
      formData.append("id", this.controleMutation.id);
      formData.append("affaire_id", this.controleMutation.affaire_id);
      if (this.controleMutation.bf_1) {
        formData.append("bf_1", this.controleMutation.bf_1);
      }
      if (this.controleMutation.bf_2) {
        formData.append("bf_2", this.controleMutation.bf_2);
      }
      if (this.controleMutation.bf_3) {
        formData.append("bf_3", this.controleMutation.bf_3);
      }
      if (this.controleMutation.bf_4) {
        formData.append("bf_4", this.controleMutation.bf_4);
      }
      if (this.controleMutation.cs_1) {
        formData.append("cs_1", this.controleMutation.cs_1);
      }
      if (this.controleMutation.cs_2) {
        formData.append("cs_2", this.controleMutation.cs_2);
      }
      if (this.controleMutation.cs_3) {
        formData.append("cs_3", this.controleMutation.cs_3);
      }
      if (this.controleMutation.cs_4) {
        formData.append("cs_4", this.controleMutation.cs_4);
      }
      if (this.controleMutation.cs_5) {
        formData.append("cs_5", this.controleMutation.cs_5);
      }
      if (this.controleMutation.od_1) {
        formData.append("od_1", this.controleMutation.od_1);
      }
      if (this.controleMutation.od_2) {
        formData.append("od_2", this.controleMutation.od_2);
      }
      if (this.controleMutation.od_3) {
        formData.append("od_3", this.controleMutation.od_3);
      }
      if (this.controleMutation.od_4) {
        formData.append("od_4", this.controleMutation.od_4);
      }
      if (this.controleMutation.od_5) {
        formData.append("od_5", this.controleMutation.od_5);
      }
      if (this.controleMutation.bat_1) {
        formData.append("bat_1", this.controleMutation.bat_1);
      }
      if (this.controleMutation.bat_2) {
        formData.append("bat_2", this.controleMutation.bat_2);
      }
      if (this.controleMutation.bat_3) {
        formData.append("bat_3", this.controleMutation.bat_3);
      }
      if (this.controleMutation.serv_1) {
        formData.append("serv_1", this.controleMutation.serv_1);
      }
      if (this.controleMutation.serv_2) {
        formData.append("serv_2", this.controleMutation.serv_2);
      }
      if (this.controleMutation.serv_3) {
        formData.append("serv_3", this.controleMutation.serv_3);
      }
      if (this.controleMutation.nom_1) {
        formData.append("nom_1", this.controleMutation.nom_1);
      }
      if (this.controleMutation.suiv_mut_1) {
        formData.append("suiv_mut_1", this.controleMutation.suiv_mut_1);
      }
      if (this.controleMutation.suiv_mut_2) {
        formData.append("suiv_mut_2", this.controleMutation.suiv_mut_2);
      }
      if (this.controleMutation.div_1) {
        formData.append("div_1", this.controleMutation.div_1);
      }
      if (this.controleMutation.div_2) {
        formData.append("div_2", this.controleMutation.div_2);
      }
      if (this.controleMutation.div_3) {
        formData.append("div_3", this.controleMutation.div_3);
      }
      if (this.controleMutation.visa) {
        formData.append("visa", this.controleMutation.visa.id);
      }
      if (this.controleMutation.date) {
        formData.append("date", moment(this.controleMutation.date, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));
      }

      this.$http
        .put(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_CONTROLE_MUTATION_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response => {
          if (response) {
            this.$root.$emit("ShowMessage", "Le formulaire de contrôle a été mis à jour avec succès")
            this.searchControleMutation();
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },
  },

  mounted: function() {
    this.searchControleMutation();
    this.searchOperateurs();

    this.affaireReadonly = !checkPermission(process.env.VUE_APP_AFFAIRE_CONTROLE_EDITION) || this.$parent.parentAffaireReadOnly;
  }
};
</script>



