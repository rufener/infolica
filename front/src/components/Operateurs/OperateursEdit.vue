<style src="./operateursEdit.css" scoped></style>
<template src="./operateursEdit.html"></template>


<script>
import { handleException } from "@/services/exceptionsHandler";
import { getCurrentDate } from "@/services/helper";

import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";

const moment = require("moment");

export default {
  name: "OperateursEdit",
  mixins: [validationMixin],
  data: () => ({
    //Mode : new or edit
    mode: "new",
    form: {
      nom: null,
      prenom: null,
      login: null,
      responsable: false,
      entree: getCurrentDate()
    },

    dataSaved: false,
    sending: false,
    lastRecord: null
  }),

  // Validations
  validations: {
    form: {
      nom: {
        required
      },
      prenom: {
        required
      },
      entree: {
        required
      },
      responsable: {
        required
      }
    }
  },

  methods: {
    /**
     * Get validation class par fieldname
     */
    getValidationClass(fieldName) {
      const field = this.$v.form[fieldName];

      if (field) {
        return {
          "md-invalid": field.$invalid && field.$dirty
        };
      }
    },

    /**
     * Clear the form
     */
    clearForm() {
      this.$v.$reset();
      this.form.nom = null;
      this.form.prenom = null;
      this.form.login = null;
      this.form.responsable = false;
      this.form.entree = getCurrentDate();
    },

    /**
     * Save data
     */
    saveData() {
      this.sending = true;
      var formData = this.initPostData();

      var url =
        process.env.VUE_APP_API_URL + process.env.VUE_APP_OPERATEURS_ENDPOINT;

      if (this.mode === "new") {
        this.$http
          .post(url, formData, {
            withCredentials: true,
            headers: { Accept: "application/json" }
          })
          .then(response => {
            this.handleSaveDataSuccess(response);
          })
          //Error
          .catch(err => {
            this.sending = false;
            handleException(err, this);
          });
      } else {
        var id = this.$route.params.id;
        formData.append("id", id);

        this.$http
          .put(url, formData, {
            withCredentials: true,
            headers: { "Content-Type": "application/x-www-form-urlencoded" }
          })
          .then(response => {
            this.handleSaveDataSuccess(response);
          })
          //Error
          .catch(err => {
            this.sending = false;
            handleException(err, this);
          });
      }
    },

    /**
     * Create formData
     */
    initPostData() {
      var formData = new FormData();

      if (this.form.nom) {
        formData.append("nom", this.form.nom);
      }
      if (this.form.prenom) {
        formData.append("prenom", this.form.prenom);
      }
      if (this.form.login) {
        formData.append("login", this.form.login);
      }
      if (this.form.responsable !== null && this.form.responsable !== undefined) {
        formData.append("responsable", this.form.responsable);
      }
      if (this.form.entree) {
        formData.append("entree",
          moment(new Date(new Date(this.form.entree))).format("YYYY-MM-DD")
        );
      }

      return formData;
    },

    /**
     * Handle save data success
     */
    handleSaveDataSuccess(response) {
      if (response && response.data) {
        this.lastRecord = `${this.form.prenom} ${this.form.nom}`;
        this.dataSaved = true;
        this.sending = false;
        this.$root.$emit("ShowMessage", "L'opérateursss " + this. lastRecord + " a été enregistré avec succès");
        this.clearForm();
      }
    },

    /**
     * Validate form
     */
    validateForm() {
      this.$v.$touch();

      if (!this.$v.$invalid) {
        this.saveData();
      }
    },

    /**
     * Cancel edit
     */
    cancelEdit() {
      this.$router.push({name: "Operateurs"});
    },

    /**
     * Init edit data
     */
    initEditData(id) {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_OPERATEURS_ENDPOINT +
            "/" +
            id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response && response.data) {
            this.form.nom = response.data.nom;
            this.form.prenom = response.data.prenom;
            this.form.login = response.data.login;
            this.form.responsable = response.data.responsable;
            this.form.entree = moment(response.data.entree, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
          }
        })
        //Error
        .catch(err => {
          this.sending = false;
          handleException(err, this);
        });
    }
  },

  mounted: function() {
    //Mode (new or edit)
    if (
      this.$router &&
      this.$router.currentRoute &&
      this.$router.currentRoute.name === "OperateursNew"
    ) {
      this.mode = "new";
    } else {
      this.mode = "edit";
    }

    //If mode = edit, get the operateur
    if (this.mode === "edit") {
      var id = this.$route.params.id;
      this.initEditData(id);
    }
  }
};
</script>

