<style src="./clientsEdit.css" scoped></style>
<template src="./clientsEdit.html"></template>


<script>
import {handleException} from '@/services/exceptionsHandler'

import { validationMixin } from 'vuelidate'
  import {
    required,
    email
  } from 'vuelidate/lib/validators'

  const moment = require('moment')

  export default {
    name: 'FormValidation',
    mixins: [validationMixin],
    data: () => ({
      //Mode : new or edit
      mode: 'new',
      clients_types_config: {
        personne_physique: Number(process.env.VUE_APP_TYPE_CLIENT_PHYSIQUE_ID),
        personne_morale: Number(process.env.VUE_APP_TYPE_CLIENT_MORAL_ID)
      },
      lastRecord: null,
      dataSaved: false,
      form: {
        type_client: 1, //default selection
        entreprise: null,
        titre: "Monsieur", //default selection
        nom: null,
        prenom: null,
        represente_par: null,
        adresse: null,
        npa: null,
        localite: null,
        case_postale: null,
        tel_fixe: null,
        fax: null,
        tel_portable: null,
        mail: null,
        entree: moment(new Date()).format(process.env.VUE_APP_DATEFORMAT_CLIENT),
        no_sap: null,
        no_bdp_bdee: null,
        co: null
      },
      sending: false,
      types_clients_list: [],
      client_moral_personnes: [],
      showDialogAddNewContact: false,
      contact_form: {
        titre: "Monsieur", //default
        nom: null,
        prenom: null,
      }
    }),

    // Validations
    validations: {
      form: {
        type_client: { required },
        entree: { required },
        mail: { email }
      }
    },
    
    methods: {

      /**
       * Get validation class par fieldname
       */
      getValidationClass (fieldName) {
        const field = this.$v.form[fieldName]

        if (field) {
          return {
            'md-invalid': field.$invalid && field.$dirty
          }
        }
      },

      /**
       * Clear the form
       */
      clearForm () {
        this.$v.$reset()
        this.form.type_client = null;
        this.form.entreprise = null;
        this.form.titre = null;
        this.form.nom = null;
        this.form.prenom = null;
        this.form.represente_par = null;
        this.form.adresse = null;
        this.form.npa = null;
        this.form.localite = null;
        this.form.case_postale = null;
        this.form.tel_fixe = null;
        this.form.fax = null;
        this.form.tel_portable = null;
        this.form.mail = null;
        this.form.entree = null;
        this.form.no_sap = null;
        this.form.no_bdp_bdee = null;
        this.form.co = null;
      },

      /*
      * Init types clients list
      */
      initTypesClientsList() {
        this.$http.get(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_SEARCH_TYPES_CLIENTS_ENDPOINT,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response =>{
          if (response && response.data) {
            this.types_clients_list = response.data;
          }
        })
        //Error 
        .catch(err => {
          handleException(err, this);
        });
      },
      
      /**
       * Save data
       */
      saveData () {
        this.sending = true;
        var formData = this.initPostData();
        
        var url = process.env.VUE_APP_API_URL + process.env.VUE_APP_CLIENTS_ENDPOINT;

        if(this.mode === 'new'){
          this.$http.post(
            url, 
            formData,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            }
          )
          .then(response =>{
            this.$router.push({ "name": "Clients" });
            this.handleSaveDataSuccess(response);
          })
          //Error 
          .catch(err => {
            this.sending = false
            handleException(err, this);
          });
        }
        else{
          var id = this.$route.params.id;
          formData.append("id", id);
          
          this.$http.put(
            url, 
            formData,
            {
              withCredentials: true,
              headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }
          )
          .then(response =>{
            this.$router.push({ "name": "Clients" });
            this.handleSaveDataSuccess(response);
          })
          //Error 
          .catch(err => {
            this.sending = false
            handleException(err, this);
          });
        }
      },

      /**
      * Handle save data success
      */
      initPostData () {
        if (this.form.co !== null && !this.form.co.startsWith("c/o ")) {
          this.form.co = "c/o " + this.form.co;
        }

        var formData = new FormData();
        formData.append("type_client", this.form.type_client);
        if (this.form.type_client === this.clients_types_config.personne_morale) {
          formData.append("entreprise", this.form.entreprise);
          formData.append("titre", null);
          formData.append("nom", null);
          formData.append("prenom", null);
        } else {
          formData.append("entreprise", null);
          formData.append("titre", this.form.titre);
          formData.append("nom", this.form.nom);
          formData.append("prenom", this.form.prenom);
        }
        formData.append("co", this.form.co || null);
        formData.append("adresse", this.form.adresse || null);
        formData.append("npa", this.form.npa || null);
        formData.append("localite", this.form.localite || null);
        formData.append("case_postale", this.form.case_postale || null);
        formData.append("tel_fixe", this.form.tel_fixe || null);
        formData.append("fax", this.form.fax || null);
        formData.append("tel_portable", this.form.tel_portable || null);
        formData.append("mail", this.form.mail || null);
        formData.append("no_sap", this.form.no_sap || null);
        formData.append("no_bdp_bdee", this.form.no_bdp_bdee || null);
        formData.append("entree", moment(this.form.entree, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));

        return formData;
      },

      /**
      * Handle save data success
      */
      handleSaveDataSuccess (response) {
        if(response && response.data){
          this.dataSaved = true;
          this.sending = false;
          this.$root.$emit("ShowMessage", "Le client a été enregistré avec succès");
          this.clearForm();
        }
      },

      /**
       * Validate form
       */
      validateForm () {
        this.$v.$touch()

        if (!this.$v.$invalid) {
          this.saveData()
        }
      },
      
      /**
       * Cancel edit
       */
      cancelEdit () {
        this.$router.push({name: "Clients"});
      },
      
      /**
       * Init edit data
       */
      initEditData (id) {
        
        this.$http.get(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_CLIENTS_ENDPOINT + '/' + id,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response =>{
          if(response && response.data){
            this.form.type_client = response.data.type_client;
            this.form.entreprise = response.data.entreprise;
            this.form.titre = response.data.titre;
            this.form.nom = response.data.nom;
            this.form.prenom = response.data.prenom;
            this.form.represente_par = response.data.represente_par;
            this.form.co = response.data.co;
            this.form.adresse = response.data.adresse;
            this.form.npa = response.data.npa;
            this.form.localite = response.data.localite;
            this.form.case_postale = response.data.case_postale;
            this.form.tel_fixe = response.data.tel_fixe;
            this.form.fax = response.data.fax;
            this.form.tel_portable = response.data.tel_portable;
            this.form.mail = response.data.mail;
            this.form.entree = moment(response.data.entree, process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
            this.form.no_sap = response.data.no_sap;
            this.form.no_bdp_bdee = response.data.no_bdp_bdee;
          }
        })
        //Error 
        .catch(err => {
          this.sending = false
          handleException(err, this);  
        });
      },

      /**
       * Init liste of people working in an entreprise
       */
      async initClientMoralPersonnes(client_id) {
        this.$http.get(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_CLIENT_MORAL_PERSONNES_ENDPOINT + "/" +
          client_id,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then(response => {
          if (response && response.data) {
            this.client_moral_personnes = response.data;
          }
        }).catch(err => this.handleException(err, this));
      },

      /**
       * Init formulaire create new contact
       */
      openContactDialog(data=null) {
        if (data === null) {
          this.contact_form = {
            id: null,
            titre: "Monsieur", //default
            nom: null,
            prenom: null,
          };
        } else {
          this.contact_form = {
            id: data.id,
            titre: data.titre,
            nom: data.nom,
            prenom: data.prenom,
          };
        }

        this.showDialogAddNewContact = true;
      },

      /**
       * Add new contact in entreprise
       */
      async editNewContactEntreprise() {
        let createMode = true;
        let formData = new FormData();
        if (this.contact_form.id !== null) {
          formData.append("id", this.contact_form.id);
          createMode = false;
        }
        formData.append("client_id", this.$route.params.id);
        formData.append("titre", this.contact_form.titre);
        formData.append("nom", this.contact_form.nom);
        formData.append("prenom", this.contact_form.prenom);

        let req = null;
        let message = "Le contact a bien été ";
        if (createMode) {
          req = this.$http.post(
            process.env.VUE_APP_API_URL +
            process.env.VUE_APP_CLIENT_MORAL_PERSONNES_ENDPOINT,
            formData,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            }
          );

          message += "enregistré";
        } else {
          req = this.$http.put(
            process.env.VUE_APP_API_URL +
            process.env.VUE_APP_CLIENT_MORAL_PERSONNES_ENDPOINT,
            formData,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            }
          );

          message += "mis à jour";
        }
        req.then(() => {
          this.$root.$emit("showMessage", message);
          this.initClientMoralPersonnes(this.$route.params.id);
          this.showDialogAddNewContact = false;
        }).catch(err => handleException(err, this));
      },

      /**
       * delete contact in entreprise
       */
      async deleteContacEntreprise(contact_id) {
        this.$http.delete(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_CLIENT_MORAL_PERSONNES_ENDPOINT +
          "?id=" + contact_id,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        ).then(() => {
          this.$root.$emit("showMessage", "Le contact a bien été supprimé");
          this.initClientMoralPersonnes(this.$route.params.id);
        }).catch(err => handleException(err, this));
      }


    },

    mounted: function(){
      this.initTypesClientsList();

      //Mode (new or edit)      
      if(this.$router && this.$router.currentRoute && this.$router.currentRoute.name === 'ClientsNew')
        this.mode = 'new';
      else
        this.mode = 'edit';


      //If mode = edit, get the client
      if(this.mode === 'edit'){
        var id = this.$route.params.id;
        this.initEditData(id);
        this.initClientMoralPersonnes(id);
      }
    }
  }

</script>

