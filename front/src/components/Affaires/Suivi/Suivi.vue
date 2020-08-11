<style src="./suivi.css" scoped></style>
<template src="./suivi.html"></template>


<script>
import { getCurrentDate, checkPermission } from "@/services/helper";
import { handleException } from "@/services/exceptionsHandler";
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";

import moment from "moment";

export default {
  name: "suivi",
  mixins: [validationMixin],
  props: {},
  components: {},
  data: () => {
    return {
      affaire_suivi: [],
      etapes_list: [],
      showNewEtapeBtn: false,
      showEtapeDialog: false,
      affaireReadonly: true,
      new_etape: {
        etape: null,
        date: getCurrentDate(),
        remarque: null
      }
    };
  },

  // Validations
  validations: {
    new_etape: {
      etape: { required },
      date: { required }
    }
  },

  methods: {
    /*
     * SEARCH AFFAIRE SUIVI
     */
    async searchAffaireSuivi() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_AFFAIRE_SUIVI_ENDPOINT +
            this.$route.params.id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response.data) {
            this.affaire_suivi = response.data;
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /*
     * SEARCH ETAPES
     */
    async searchEtapes() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_ETAPES_INDEX_ENDPOINT,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response.data) {
            this.etapes_list = response.data.map(x => ({
              id: x.id,
              nom: x.nom,
              toLowerCase: () => x.nom.toLowerCase(),
              toString: () => x.nom
            }));
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Enregistrer une nouvelle étape
     */
    saveNewEtape: function() {
      var formData = new FormData();
      formData.append("affaire_id", this.$route.params.id);
      if (this.new_etape.etape.id) {
        formData.append("etape_id", this.new_etape.etape.id);
      }
      if (this.new_etape.date) {
        formData.append("date",
          moment(this.new_etape.date, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS)
        );
      }
      if (this.new_etape.remarque) {
        formData.append("remarque", this.new_etape.remarque);
      }

      this.$http
        .post(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_AFFAIRE_ETAPES_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response.data) {
            this.searchAffaireSuivi();
            // handle success
            this.$root.$emit("ShowMessage", "Le suivi a été enregistré avec succès")
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Confirmer l'édition d'état
     */
    onConfirmEditEtape: function() {
      this.$v.$touch();
      if (!this.$v.$invalid) {
        this.saveNewEtape();
        this.initForm();
      }
    },

    /**
     * Annuler l'édition d'état
     */
    onCancelEditEtape: function() {
      this.initForm();
    },

    /**
     * Clear form
     */
    initForm() {
      this.$v.$reset();
      this.showEtapeDialog = false;
      this.new_etape.etape = null;
      this.new_etape.date = getCurrentDate();
      this.new_etape.remarque = null;
    },

    /*
     * Get validation class par fieldname
     */
    getValidationClass(fieldName) {
      const field = this.$v.new_etape[fieldName];

      if (field) {
        return {
          "md-invalid": field.$invalid && field.$dirty
        };
      }
    }
  },

  mounted: function() {
    this.searchAffaireSuivi();
    this.searchEtapes();
    this.initForm();

    this.affaireReadonly = !checkPermission(process.env.VUE_APP_AFFAIRE_SUIVI_EDITION) || this.$parent.parentAffaireReadOnly;
  }
};
</script>



