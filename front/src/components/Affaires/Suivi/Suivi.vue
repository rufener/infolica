<style src="./suivi.css" scoped></style>
<style lang="css">.md-menu-content { z-index: 9000 !important; }</style>
<template src="./suivi.html"></template>


<script>
import { getCurrentDate, checkPermission, stringifyAutocomplete } from "@/services/helper";
import { handleException } from "@/services/exceptionsHandler";
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";

import moment from "moment";

export default {
  name: "suivi",
  mixins: [validationMixin],
  data: () => {
    return {
      affaire_suivi: [],
      affaire_suivi_bk: [],
      etapes_list: [],
      showNewEtapeBtn: false,
      showEtapeDialog: false,
      affaireReadonly: true,
      new_etape: {
        etape: null,
        date: getCurrentDate(),
        remarque: null
      },
      cb_showDetail: false
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
            let tmp = response.data;

            // set date format and sort by date
            let max_next_datetime_sort = 0;
            tmp.forEach(x => {
              x.next_datetime_sort = new Date(x.next_datetime).getTime();
              if (max_next_datetime_sort < x.next_datetime_sort) {
                max_next_datetime_sort = x.next_datetime_sort;
              }
              x.datetime = x.datetime? moment(new Date(x.datetime)).format(process.env.VUE_APP_DATEFORMAT_CLIENT): null;
              x.next_datetime = x.next_datetime? moment(new Date(x.next_datetime)).format(process.env.VUE_APP_DATEFORMAT_CLIENT): null;

              // custom realisation's period to show
              if (x.etape_priorite === 1) {
                if (x.datetime && x.next_datetime) {
                  x.realisation_period_txt = x.datetime + " - " + x.next_datetime;
                } else {
                  if (x.etape_id) {
                    if (x.etape_id === Number(process.env.VUE_APP_FIN_PROCESSUS_ID)) {
                      x.realisation_period_txt = x.datetime;
                    } else {
                      x.realisation_period_txt = x.datetime + " - ...";
                    }
                  }
                  else {
                    x.realisation_period_txt = x.next_datetime;
                  }
                }
              } else {
                // priority 2
                x.realisation_period_txt = x.datetime;
              }
              });

            let primaryKeys = [];
            tmp.forEach(x => {
              // fix duplicate primary key due to duplicate first step (see view in database)
              if (primaryKeys.includes(x.id)) {
                x.id = 0;
              }
              primaryKeys.push(x.id);

              // set sort by date value where it is null
              if (x.next_datetime_sort === 0) {
                x.next_datetime_sort = max_next_datetime_sort + 1;
              }
            });


            this.affaire_suivi_bk = tmp;
            this.updateAffaireSuiviShowList();
          }
        })
        .catch(err => handleException(err, this));
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
          if (response && response.data) {
            this.etapes_list = stringifyAutocomplete(response.data);
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
    },

    /**
     * Update list of suivi affaire list on set priority
     */
    updateAffaireSuiviShowList() {
      if (this.cb_showDetail) {
        this.affaire_suivi = this.affaire_suivi_bk;
      } else {
        this.affaire_suivi = this.affaire_suivi_bk.filter(x => x.etape_priorite === 1);
      }
    }
  },

  mounted: function() {
    this.searchAffaireSuivi();
    this.searchEtapes();
    this.initForm();

    // Event listener
    this.$root.$on('getAffaireSuivi', () => this.searchAffaireSuivi());

    this.affaireReadonly = !checkPermission(process.env.VUE_APP_AFFAIRE_SUIVI_EDITION) || this.$parent.parentAffaireReadOnly;
  }
};
</script>



