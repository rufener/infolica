<style src="./preavis.css" scoped></style>
<template src="./preavis.html"></template>


<script>
import { getCurrentDate, checkPermission, getDocument } from "@/services/helper";
import { handleException } from "@/services/exceptionsHandler";
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
import moment from "moment";

export default {
  name: "preavis",
  mixins: [validationMixin],
  props: {},
  components: {},
  data: () => {
    return {
      affaire_preavis: [],
      preavis_type_liste: [],
      services_liste: [],
      services_liste_bk: [],
      lastRecord: null,
      showNewPreavisBtn: false,
      showPreavisDialog: false,
      modifyPreavis: false,
      affaireReadonly: true,
      new_preavis: {
        id: null,
        service: null,
        preavis: null,
        date_demande: getCurrentDate(),
        date_reponse: null,
        remarque: null
      }
    };
  },

  // Validations
  validations: {
    new_preavis: {
      service: { required },
      date_demande: { required }
    }
  },

  methods: {
    /*
     * SEARCH AFFAIRE PREAVIS
     */
    async searchAffairePreavis() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_AFFAIRE_PREAVIS_ENDPOINT +
            this.$route.params.id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response.data) {
            this.affaire_preavis = response.data;
            if (this.affaire_preavis.date_demande) {
              this.affaire_preavis.date_demande = moment(this.affaire_preavis.date_demande, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
            }
            if (this.affaire_preavis.date_reponse) {
              this.affaire_preavis.date_reponse = moment(this.affaire_preavis.date_reponse, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
            }
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /*
     * SEARCH PREAVIS TYPES
     */
    async searchPreavisType() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_PREAVIS_TYPE_ENDPOINT,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response.data) {
            this.preavis_type_liste = response.data.map(x => ({
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

    /*
     * SEARCH SERVICES
     */
    async searchServices() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_SERVICES_ENDPOINT,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response.data) {
            this.services_liste_bk = response.data;
            this.services_liste = response.data.map(x => ({
              id: x.id,
              nom: x.abreviation,
              toLowerCase: () => x.abreviation.toLowerCase(),
              toString: () => x.abreviation
            }));
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Modifier un préavis existant
     */
    onModifyPreavis: function(curr_preavis) {
      this.new_preavis.id = curr_preavis.id;
      this.new_preavis.date_demande = moment(curr_preavis.date_demande, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
      if (curr_preavis.date_reponse) {
        this.new_preavis.date_reponse = moment(curr_preavis.date_reponse, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
      } else {
        // si pas de date de réponse, proposition défaut aujourd'hui
        this.new_preavis.date_reponse = moment(new Date()).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
        }
      // this.new_preavis.date_reponse = curr_preavis.date_reponse;
      this.new_preavis.remarque = curr_preavis.remarque;
      this.new_preavis.service = this.services_liste
        .filter(data => data.nom === curr_preavis.service)
        .map(x => ({
          id: x.id,
          nom: x.nom,
          toLowerCase: () => x.nom.toLowerCase(),
          toString: () => x.nom
        }))[0];
      if (curr_preavis) {
        this.new_preavis.preavis = this.preavis_type_liste
          .filter(data => data.nom === curr_preavis.preavis)
          .map(x => ({
            id: x.id,
            nom: x.nom,
            toLowerCase: () => x.nom.toLowerCase(),
            toString: () => x.nom
          }))[0];
      }
      this.modifyPreavis = true;
      this.showPreavisDialog = true;
    },

    /**
     * Confirmer l'édition de préavis
     */
    onConfirmEditPreavis: function() {
      this.$v.$touch();

      if (!this.$v.$invalid) {
        this.saveNewPreavis();
        this.clearForm();
      }
    },

    /**
     * Enregistrer une nouvelle étape
     */
    saveNewPreavis: function() {
      var formData = this.fillData();

      var req;
      // Modification de préavis
      if (this.modifyPreavis) {
        req = this.$http.put(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_PREAVIS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        );
      } else {
        // Création d'un nouveau préavis
        req = this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_PREAVIS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        );
      }
      req
        .then(response => {
          if (response.data) {
            this.searchAffairePreavis();
            // handle success
            this.$root.$emit("ShowMessage", "Le préavis au " + this.lastRecord + " a été enregistrée avec succès")
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Fill formData pour la requête post ou put
     */
    fillData() {
      var formData = new FormData();
      formData.append("affaire_id", this.$route.params.id);
      if (this.new_preavis.service.id) {
        formData.append("service_id", this.new_preavis.service.id);
        this.lastRecord = this.new_preavis.service.nom;
      }
      if (this.new_preavis.preavis) {
        formData.append("preavis_type_id", this.new_preavis.preavis.id);
      }
      if (this.new_preavis.date_demande) {
        formData.append("date_demande",
          moment(this.new_preavis.date_demande, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));
      }
      if (this.new_preavis.date_reponse) {
        formData.append("date_reponse",
          moment(this.new_preavis.date_reponse, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));
      }
      if (this.new_preavis.remarque) {
        formData.append("remarque", this.new_preavis.remarque);
      }
      if (this.new_preavis.id){
        formData.append("id", this.new_preavis.id);
      }

      return formData;
    },

    /**
     * Annuler l'édition d'état
     */
    onCancelEditPreavis: function() {
      this.clearForm();
    },

    /**
     * Clear form
     */
    clearForm() {
      this.$v.$reset();
      this.showPreavisDialog = false;
      this.new_preavis.id = null;
      this.new_preavis.service = null;
      this.new_preavis.preavis = null;
      this.new_preavis.date_demande = getCurrentDate();
      this.new_preavis.date_reponse = null;
      this.new_preavis.remarque = null;
      this.modifyPreavis = false;
    },

    /*
     * Get validation class par fieldname
     */
    getValidationClass(fieldName) {
      const field = this.$v.new_preavis[fieldName];

      if (field) {
        return {
          "md-invalid": field.$invalid && field.$dirty
        };
      }
    },

    /**
     * Validate form
     */
    validateForm() {
      this.$v.$touch();

      if (!this.$v.$invalid) {
        this.onConfirmEditPreavis();
      }
    },

    /**
     * getModel pour préavis
     */
    async downloadModel(service_id) {
      let form = {};

      const service_ = this.services_liste_bk.filter(x => x.id === service_id).pop();
      form.adresse_service = [
        service_.service,
        service_.adresse,
        [service_.npa, service_.localite].filter(Boolean).join(" ")
      ].filter(Boolean).join("\n");

      const affaire_ = this.$parent.affaire;
      form.adresse_demandeur = [
        affaire_.client_commande_entreprise,
        [affaire_.client_commande_titre, affaire_.client_commande_prenom, affaire_.client_commande_nom].filter(Boolean).join(" "),
        affaire_.client_commande_adresse,
        affaire_.client_commande_case_postale,
        [affaire_.client_commande_npa, affaire_.client_commande_localite].filter(Boolean).join(" ")
      ].filter(Boolean).join("\n");
      
      let observation = {
        titre: "",
        contenu: ""
      };
      if (service_id === Number(process.env.VUE_APP_SERVICE_SCAT)) {
        observation.titre = "Observation:",
        observation.contenu = "Pour autant que vous le jugiez utile, veuillez transmettre le dossier au service des forêts ou au service de la viticulture."
      }

      let formData = new FormData();
      formData.append("template", "Preavis")
      formData.append("output_file_name", service_.abreviation)
      formData.append("values", JSON.stringify({
        ADRESSE_SERVICE: form.adresse_service,
        DATE_ENVOI: String(getCurrentDate()),
        NREF: affaire_.id,
        DATE_DEMANDE: String(affaire_.date_ouverture),
        ADRESSE_DEMANDEUR: form.adresse_demandeur,
        CADASTRE: affaire_.cadastre,
        CONCERNE: affaire_.nom,
        OBSERVATION_TITRE: observation.titre,
        OBSERVATION: observation.contenu,
        ANNEXES: ""
      }));

      getDocument(formData)
      .then(response => {
          this.$root.$emit("ShowMessage", "Le fichier '" + response + " se trouve dans le dossier 'Téléchargement'")
      })
      .catch(err => handleException(err, this));
    }
  },

  mounted: function() {
    this.searchAffairePreavis();
    this.searchPreavisType();
    this.searchServices();

    this.affaireReadonly = !checkPermission(process.env.VUE_APP_AFFAIRE_PREAVIS_EDITION) || this.$parent.parentAffaireReadOnly;
  }
};
</script>



