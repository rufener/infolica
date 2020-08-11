<template src="./clotureAffaire.html"></template>


<script>
import { handleException } from "@/services/exceptionsHandler";
import { getEtatsNumeros, stringifyAutocomplete } from "@/services/helper.js";
import moment from "moment";

export default {
  name: "ClotureAffaire",
  props: {},
  component: {},
  data: () => {
    return {
      showClotureDialog: false,
      affaire_numeros: [],
      numero_etats_liste: []
    };
  },
  methods: {
    /**
     * Open clotureDialog
     */
    openClotureDialog(){
      this.getNumerosAffaire();
      this.showClotureDialog = true;
    },

    /**
     * Charger les numéros dans l'affaire
     */
    async getNumerosAffaire() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_AFFAIRE_NUMEROS_ENDPOINT +
          this.$route.params.id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response && response.data) {
            var numeros_base_liste = this.getNumerosBaseList(response.data);
            var affaire_numeros_tmp = this.filterNumerosActiveInAffaire(response.data);
            this.affaire_numeros = this.setPredictedFutureState(affaire_numeros_tmp, numeros_base_liste);
          }
        })
        .catch(err => handleException(err, this));
    },

    /**
     * Récupérer les numéros de base pour les numéros DDP, PPE et PCOP
     */
    getNumerosBaseList(data) {
      var tmp = new Set(data.map(x => x.numero_base_id));
      tmp.delete(null);
      return Array.from(tmp);
    },

    /**
     * Filtrer les numéros actifs dans l'affaire
     */
    filterNumerosActiveInAffaire(numeros) {
      return numeros.filter(x => x.affaire_destination_id === null);
    },

    /**
     * Créer la prédiction de l'état du numéro
     */
    setPredictedFutureState(data, base) {
      
      let num_type = {
        ancien_id: Number(process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_ANCIEN_ID),
        nouveau_id: Number(process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_NOUVEAU_ID)
      };
      
      let num_etat = {
        projet_id: Number(process.env.VUE_APP_NUMERO_PROJET_ID),
        vigueur_id: Number(process.env.VUE_APP_NUMERO_VIGUEUR_ID),
        supprime_id: Number(process.env.VUE_APP_NUMERO_SUPPRIME_ID)
      };

      data.forEach(element => {
        element.numero_etatFutur_id = element.numero_etat_id;

        // Cas des numéros projetés, non mat-diff, à passer de projet à validé
        if (element.affaire_numero_type_id === num_type.nouveau_id && 
            element.numero_etat_id === num_etat.projet_id) {
          element.numero_etatFutur_id = num_etat.vigueur_id;
        } 
        // Cas des numéros référencés à supprimer
        else if (element.affaire_numero_type_id === num_type.ancien_id) {
          if (~base.includes(element.numero_id)) {
            element.numero_etatFutur_id = num_etat.supprime_id;
          }
        }
      });
      return data;
    },

    /**
     * Récupérer les états des numéros
     */
    async getNumeroEtats() {
      getEtatsNumeros()
      .then(response => {
        if (response && response.data) {
          this.numero_etats_liste = stringifyAutocomplete(response.data);
        }
      })
      .catch(err => handleException(err, this));
    },

    /**
     * update Affaire_Numeros when new etat selected
     */
    updateAffaireNumero(num_id, etat_id) {
      this.affaire_numeros.map(x => {
        if (x.numero_id == num_id) {
          x.numero_etatFutur_id = etat_id;
        } 
      })
    },


    /**
     * Confirmer la clôture d'affaire
     */
    onConfirmCloture() {
      this.showClotureDialog = false;
      
      const _this = this;
      var promises = [];

      _this.affaire_numeros.forEach(num => {
        promises.push(_this.saveNewEtatNumero(num));
        promises.push(_this.saveNewEtatHistoryNumero(num));
      });

      Promise.all(promises)
      .then(response => {
        if (response) {
          this.AjoutDateClotureAffaire()
          .then(() => {
            this.$router.go(0);
            this.$parent.setAffaire(); 
            this.$root.$emit("ShowMessage", "L'affaire " + this.$route.params.id + " a été clôturées avec succès");         
          })
          .catch(err => handleException(err, this));
        }
      })
      .catch(err => {
        handleException(err, this);
      });
    },

    /**
     * Ajout de la date de clôture de l'affaire
     */
    async AjoutDateClotureAffaire(){
      return new Promise((resolve, reject) => {
        var formData = new FormData();
        formData.append("id_affaire", this.$route.params.id);
        formData.append("date_cloture",  moment(new Date()).format(process.env.VUE_APP_DATEFORMAT_WS));

        this.$http
          .put(
            process.env.VUE_APP_API_URL +
            process.env.VUE_APP_AFFAIRES_ENDPOINT,
            formData,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            }
          ).then(response => {
            if (response) {
              resolve(response);
            }
          }).catch(err => reject(err));
        })
    },


    /**
     * Enregistrer le nouvel état des numéros
     */
    async saveNewEtatNumero(num) {
      var formData = new FormData();
      formData.append("id", num.numero_id);
      formData.append("etat_id", num.numero_etatFutur_id);

      return new Promise((resolve, reject) => {
        this.$http.put(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_NUMEROS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        )
        .then(response => resolve(response))
        .catch(err => reject(err));
      })
    },

    /**
     * Enregistrer l'historique du changement d'état du numéro
     */
    async saveNewEtatHistoryNumero(num) {
      var formData = new FormData();
      formData.append("numero_id", num.numero_id);
      formData.append("numero_etat_id", num.numero_etatFutur_id);
      formData.append("date", moment(new Date()).format(process.env.VUE_APP_DATEFORMAT_WS));
      
      return new Promise((resolve, reject) => {
        this.$http.post(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_NUMEROS_ETAT_HISTO_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        )
        .then(response => resolve(response))
        .catch(err => reject(err));
      })
    },


  },
  mounted: function() {
    this.getNumeroEtats();
  }
};
</script>