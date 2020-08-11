<style src="./newAffaire.css" scoped></style>
<template src="./newAffaire.html"></template>


<script>
import MapHandler from "@/components/MapHandler/MapHandler.vue";
import { validationMixin } from "vuelidate";
import { handleException } from "@/services/exceptionsHandler";
import { required } from "vuelidate/lib/validators";
import { getCurrentDate,
         getClients,
         filterList,
         stringifyAutocomplete } from "@/services/helper";
import Autocomplete from "vuejs-auto-complete";
const moment = require("moment");
export default {
  name: "NewAffaire",
  mixins: [validationMixin],
  props: {},
  components: {
    MapHandler,
    Autocomplete
  },
  data: () => {
    return {
      affaire_numeros_anciens: [],
      affaire_numeros_nouveaux: [],
      cadastres_list: [],
      client_facture: null,
      client_facture_co: null,
      client_facture_complement: null,
      client_facture_premiere_ligne: null,
      clients_list: [],
      clients_liste_type: [],
      client_moral_personnes: {
        commande: [],
        envoi: [],
        facture: []
      },
      clients_types_config: {
        personne_morale: Number(process.env.VUE_APP_TYPE_CLIENT_MORAL_ID),
        personne_physique: Number(process.env.VUE_APP_TYPE_CLIENT_PHYSIQUE_ID)
      },
      dataSaved: false,
      form: {
        affaire_base: null,
        affaire_base_id: null,
        affaire_modif_type: null,
        cadastre: null,
        client_commande: null,
        client_commande_complement: null,
        client_envoi: null,
        client_envoi_complement: null,
        date_cloture: null,
        date_ouverture: moment(new Date()).format(process.env.VUE_APP_DATEFORMAT_CLIENT),
        date_validation: null,
        localisation: null,
        localisation_E: null,
        localisation_N: null,
        nom: null,
        remarque: null,
        technicien_id: null,
        type: null,
        vref: null
      },
      lastRecord: null,
      operateurs_list: [],
      search_clients_list: [],
      selectedAnciensNumeros: [],
      selectedModificationAffaire: null,
      selectedNouveauxNumeros: [],
      sending: false,
      showClientsForm: true,
      show_co: false,
      sitn_search_categories: null,
      types_affaires_list: [],
      type_modification_bool: false,
      typesModficiationAffaire_list: []
    };
  },
  // Validations
  validations() {
    let form = {};
    let client_facture = {};
    let client_facture_co = {};

    if (this.showClientsForm) {
      form = {
        type: {required},
        technicien_id: {required},
        cadastre: {required},
        date_ouverture: {required},
        localisation: {required},
        client_commande: {required},
        client_envoi: {required}
      };

      client_facture = {
        id: {required}
      };
  
      if (this.show_co) {
        client_facture_co = {
          id : { required }
        }
      }

    } else {
      form = {
        type: {required},
        technicien_id: {required},
        cadastre: {required},
        date_ouverture: {required},
        localisation: {required}
      };
    }

    if (this.type_modification_bool) {
      form.affaire_modif_type = {required}  
    }

    return {form, client_facture, client_facture_co}
  },

  methods: {
    /**
     * Get validation class par fieldname pour objet form
     */
    getValidationClass(field) {
      if (field) {
        return {
          "md-invalid": field.$invalid && field.$dirty
        };
      }
    },

    /**
     * Init map
     */
    callInitMap: function() {
      var defaultCenter = JSON.parse(process.env.VUE_APP_MAP_DEFAULT_CENTER);
      this.$refs.mapHandler.initMap(
        defaultCenter,
        process.env.VUE_APP_MAP_DEFAULT_ZOOM
      );
      this.$refs.mapHandler.map.on("singleclick", this.onMapClick(this));
      this.$refs.mapHandler.modify.on("modifyend", this.onFeatureChange(this));
    },

    /**
     * Handle map feature change event
     */
    onFeatureChange: function(_this) {
      return function(modify) {
        const features = modify.features.getArray();
        if (features) {
          const feature = features[0];
          const coordinates = feature.getGeometry().getCoordinates();
          _this.form.localisation_E = coordinates[0];
          _this.form.localisation_N = coordinates[1];
          _this.handleLocalisation(_this.form.localisation_E, _this.form.localisation_N);
        }
      };
    },

    /**
     * Handle map click event
     */
    onMapClick: function(_this) {
      return function(evt) {
        if (evt.coordinate) {
          _this.form.localisation_E = evt.coordinate[0];
          _this.form.localisation_N = evt.coordinate[1];
          _this.handleLocalisation(_this.form.localisation_E, _this.form.localisation_N);
        }
      };
    },

    /**
     * Handle localisation
     */
    handleLocalisation: function(localisation_E, localisation_N, zoom) {
      this.$refs.mapHandler.clearMarkers();
      this.form.localisation = [
        Math.round(localisation_E),
        Math.round(localisation_N)
      ].join(" / ");
      this.$refs.mapHandler.addMarker(
        localisation_E,
        localisation_N,
        zoom
      );
    },

    /*
     * Init types affaires list
     */
    async initTypesAffairesList() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_TYPES_AFFAIRES_ENDPOINT,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response && response.data) {
            this.types_affaires_list = stringifyAutocomplete(response.data);
          }
        })
        //Error
        .catch(err => {
          handleException(err, this);
        });
    },

    /*
     * Init clients list
     */
    async initClientsList() {
      getClients()
      .then(response => {
        if (response && response.data) {
          this.clients_list = stringifyAutocomplete(response.data, "adresse_");
          this.clients_liste_type = response.data.map(x => ({
            id: x.id,
            type_id: x.type_client
          }));
          
          this.updateContact();
        }
      })
      //Error
      .catch(err => {
        handleException(err, this);
      });
    },

    /*
     * Init operateurs list
     */
    async initOperateursList() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_OPERATEURS_ENDPOINT,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response && response.data) {
            var tmp = response.data.map(x => ({
              id: x.id,
              nom: [x.prenom, x.nom].join(" "),
              responsable: x.responsable,
              toLowerCase: () => [x.prenom, x.nom].join(" ").toLowerCase(),
              toString: () => [x.prenom, x.nom].join(" ")
            }));
            this.operateurs_list = tmp;
            this.form.technicien_id = JSON.parse(
              localStorage.getItem("infolica_user")
            ).id;
          }
        })
        //Error
        .catch(err => {
          handleException(err, this);
        });
    },

    /*
     * Init cadastres list
     */
    async initCadastresList() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_CADASTRES_ENDPOINT,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response && response.data) {
            this.cadastres_list = stringifyAutocomplete(response.data);
          }
        })
        //Error
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Search Client after 3 letters
     */
    searchClients(value) {
      this.search_clients_list = filterList(this.clients_list, value, 3);
    },

    /**
     * Save data
     */
    saveData() {
      this.sending = true;
      var formData = this.initPostData();
      var url =
        process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRES_ENDPOINT;
      this.$http
        .post(url, formData, {
          withCredentials: true,
          headers: { Accept: "application/json" }
        })
        .then(response => {
          const _response = response;
          const id_new_affaire = response.data;
          if (response && response.data) {
            var promises = [];
            // Enregistrer une facture vide
            if (this.showClientsForm){
              promises.push(this.postFacture(id_new_affaire));
            } 
            if (this.form.remarque !== null) {
              promises.push(this.postRemarqueAffaire(id_new_affaire));
            }
            if (this.type_modification_bool) {
              promises.push(this.postAffaireRelation(id_new_affaire));
              if ((this.selectedAnciensNumeros.length + this.selectedNouveauxNumeros.length) > 0 ) {
                promises.push(this.updateNumerosAffaire(id_new_affaire));
              }
            }
            Promise.all(promises)
            .then(() => {
              this.handleSaveDataSuccess(_response);
              this.$router.push({
                name: "AffairesDashboard",
                params: { id: id_new_affaire }
              });

            }).catch(err => {
                handleException(err, this);
                this.sending = false;
              });

          }
        })
        //Error
        .catch(err => {
          this.sending = false;
          handleException(err, this);
        });
    },

    /**
     * Enregistre une facture vide avec l'adresse
     */
    postFacture(affaire_id) {
      return new Promise((resolve, reject) => {
        var formData = new FormData();
        formData.append("affaire_id", affaire_id);
        formData.append("client_id", this.client_facture.id);
        if (this.client_facture_complement !== null) {
          formData.append("client_complement", "À l'att. de " + this.client_facture_complement);
        }
        if (this.client_facture_premiere_ligne !== null) {
          formData.append("client_premiere_ligne", this.client_facture_premiere_ligne);
        }
        if (this.show_co && this.client_facture_co !== null && this.client_facture_co.id !== null) {
          formData.append("client_co_id", this.client_facture_co.id);
        }
        this.$http
          .post(
            process.env.VUE_APP_API_URL + process.env.VUE_APP_FACTURE_ENDPOINT,
            formData,
            {
              withCredentials: true,
              headers: { Accept: "applicatoin/json" }
            }
          )
          .then(response => {
            if (response && response.data) {
              this.$root.$emit(
                "ShowMessage",
                "Une facture a correctement été créée dans l'affaire"
              );
              resolve(response);
            }
          })
          .catch(err => reject(err));
      });
    },

    /**
     * Post affaires relation si affaire de type modification
     */
    postAffaireRelation(affaire_id) {
      var formData = new FormData();
      formData.append('affaire_id_mere', this.form.affaire_base_id);
      formData.append('affaire_id_fille', affaire_id);
      formData.append('type_id', this.form.affaire_modif_type.id);
      formData.append("date", moment(getCurrentDate(), process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));
      return new Promise((resolve, reject) => {
        this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_MODIFICATION_AFFAIRE_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => reject(err));
      })
    },

    /**
     * Post remarque affaire si remarque spécifiée
     */
    postRemarqueAffaire(affaire_id) {
      var formData = new FormData();
      formData.append("affaire_id", affaire_id);
      formData.append("remarque", this.form.remarque);
      formData.append("operateur_id", this.form.technicien_id);
      formData.append("date", moment(getCurrentDate(), process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));

      return new Promise((resolve, reject) => {
        this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_REMARQUES_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => reject(err));
      });
    },

    /**
     * Handle save data success
     */
    initPostData() {
      var formData = new FormData();
      formData.append("type_id", this.form.type.id);
      if (this.form.nom) {
        formData.append("nom", this.form.nom);
      }
      if (this.form.client_commande && this.form.client_commande.id) {
        formData.append("client_commande_id", this.form.client_commande.id);
      }
      if (this.form.client_commande_complement && this.showClientComplement(this.form.client_commande)) {
        formData.append("client_commande_complement", "À l'att. de " + this.form.client_commande_complement);
      }
      if (this.form.client_envoi && this.form.client_envoi.id) {
        formData.append("client_envoi_id", this.form.client_envoi.id);
      }
      if (this.form.client_envoi_complement && this.showClientComplement(this.form.client_envoi)) {
        formData.append("client_envoi_complement", "À l'att. de " + this.form.client_envoi_complement);
      }
      if (this.form.technicien_id) {
        formData.append("technicien_id", this.form.technicien_id);
      }
      if (this.form.cadastre && this.form.cadastre.id) {
        formData.append("cadastre_id", this.form.cadastre.id);
      }
      if (this.form.localisation_E) {
        formData.append("localisation_E", this.form.localisation_E);
      }
      if (this.form.localisation_N) {
        formData.append("localisation_N", this.form.localisation_N);
      }
      if (this.form.vref) {
        formData.append("vref", this.form.vref);
      }
      if (this.form.date_ouverture) {
        formData.append("date_ouverture",
          moment(this.form.date_ouverture, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS)
        );
      }
      if (this.form.date_validation) {
        formData.append("date_validation",
          moment(this.form.date_validation, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS)
        );
      }
      if (this.form.date_cloture) {
        formData.append("date_cloture",
          moment(this.form.date_cloture, process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS)
        );
      }
      return formData;
    },

    /**
     * Update numeros_affaire
     */
    updateNumerosAffaire(affaire_destination_id) {
      let promises = [];
      this.selectedAnciensNumeros.forEach(x => {
        promises.push(this.deactivateNumeroAffaires(x, affaire_destination_id));
        promises.push(this.postAffaireNumero(x, affaire_destination_id));
      });
      this.selectedNouveauxNumeros.forEach(x => {
        promises.push(this.deactivateNumeroAffaires(x, affaire_destination_id));
        promises.push(this.postAffaireNumero(x, affaire_destination_id));
        promises.push(this.updateNumeroRelation(x.numero_base_id, x.numero_id, x.affaire_id, affaire_destination_id));
      });

      Promise.all(promises)
      .then(() => this.$root.$emit("ShowMessage", "Les numéros ont bien été récupérés de l'affaire de base"))
      .catch(err => handleException(err, this));
    },

    /**
     * desactiver_numeros_affaires dans affaire base
     */
    async deactivateNumeroAffaires(affnum, affaire_destination_id) {
      let formData = new FormData();
      formData.append("id", affnum.id);
      formData.append("actif", false);
      formData.append("affaire_destination_id", affaire_destination_id);

      return new Promise ((resolve, reject) => {
        this.$http.put(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_NUMEROS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => reject(err));
      });
    },

    /**
     * Update numero_relation
     */
    async updateNumeroRelation(num_base_id, num_associe_id, old_affaire_id, new_affaire_id) {
      let formData = new FormData();
      formData.append("numero_id_base", num_base_id);
      formData.append("numero_id_associe", num_associe_id);
      formData.append("affaire_old_id", old_affaire_id);
      formData.append("affaire_new_id", new_affaire_id);

      return new Promise((resolve, reject) => {
        this.$http.put(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_NUMEROS_RELATIONS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => reject(err));
      })
    },

    /**
     * Create new numero_affaire relation
     */
    async postAffaireNumero(affnum, affaire_destination_id) {
      var formData = new FormData();
      formData.append("affaire_id", affaire_destination_id);
      formData.append("numero_id", affnum.numero_id);
      formData.append("type_id", affnum.affaire_numero_type_id);
      formData.append("actif", true);

      return new Promise((resolve, reject) => {
        this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_NUMEROS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => reject(err));
      });
    },

    /**
     * Handle save data success
     */
    handleSaveDataSuccess(response) {
      if (response && response.data) {
        this.lastRecord = `${this.form.nom}`;
        this.dataSaved = true;
        this.sending = false;
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
      this.$router.push({ name: "Affaires" });
    },

    /**
     * User SITN search service
     */
    async doSearchSITN(input) {
      let result = await this.$http
        .get(process.env.VUE_APP_SITN_SEARCH_SERVICE_URL + input)
        .then(response => {
          return response;
        })
        //Error
        .catch(err => {
          this.sending = false;
          console.error(err);
        });
      return result;
    },

    /**
     * Search SITN endpoint
     */
    searchSITNEndpoint(input) {
      let cadastre_ = null;
      if (this.form.cadastre.id !== null) {
        cadastre_ = this.cadastres_list.filter(
          x => x.id === this.form.cadastre.id
        )[0].nom;
      }

      return (
        process.env.VUE_APP_SITN_SEARCH_SERVICE_URL +
        [input, cadastre_, "egrid"].filter(Boolean).join(" ")
      );
    },

    /**
     * Handle SITN search item
     */
    handleSelectSITNItem(feature) {
      if (
        feature &&
        feature.selectedObject &&
        feature.selectedObject.geometry
      ) {
        this.$refs.mapHandler.addGraphic(feature.selectedObject);
      }
      // access the autocomplete component methods from the parent
      this.$refs.autocomplete.clear();
    },

    /**
     * Handle display format
     */
    formattedDisplay(result) {
      return result.properties.label;
    },

    /**
     * Complète par défaut les clients envoi et facture
     */
    defaultCompleteClients(client) {
      this.initClientMoralPersonnes(client.id, 'commande').then(() => {
        if (this.form.client_envoi === null || this.form.client_envoi === "") {
          this.form.client_envoi = client;
          this.client_moral_personnes.envoi = this.client_moral_personnes.commande;
        }
        if (this.client_facture === null || this.client_facture === "") {
          this.client_facture = client;
          this.client_moral_personnes.facture = this.client_moral_personnes.commande;
        }
      });
    },

    /**
     * openCreateClient
     */
    openCreateClient() {
      let routedata = this.$router.resolve({ name: "ClientsNew" });
      window.open(routedata.href, "_blank");
    },

    /**
     * On Select Type affaire
     */
    onSelectType() {
      if (this.form.type.id === Number(process.env.VUE_APP_TYPE_AFFAIRE_MODIFICATION)){
        this.type_modification_bool = true;
      } else {
        this.type_modification_bool = false;
      }
      // this.showClientsForm = this.form.type_id === Number(process.env.VUE_APP_TYPE_AFFAIRE_CADASTRATION)? false: true;
      if (this.form.type.id === Number(process.env.VUE_APP_TYPE_AFFAIRE_CADASTRATION)) {
        this.showClientsForm = false;
        this.form.client_commande = null;
        this.form.client_envoi = null;
        this.form.client_envoi_complement = null;
        this.client_facture = null;
        this.client_facture_complement = null;
        this.client_facture_premiere_ligne = null;
      } else {
        this.showClientsForm = true;
      }
    },

    /**
     * get Types de modifications d'affaire
     */
    async initTypesModficiationAffaire() {
      this.$http.get(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_TYPES_MODIF_AFFAIRE_ENDPOINT,
        {
          withCredentials: true,
          headers: {Accept: "application/json"}
        }
      ).then(response => {
        if (response && response.data) {
          this.typesModficiationAffaire_list = stringifyAutocomplete(response.data)
        }
      }).catch(err => handleException(err, this));
    },

    /*
     * Open affaire modification in new tab
     */
    doOpenAffaireModification() {
      const routeData = this.$router.resolve({ name: "AffairesDashboard", params: {id: this.form.affaire_base_id}});
      window.open(routeData.href, '_blank');
    },

     /**
     * Select affaire modification
     */
    doSelectAffaireModification() {
      let _this = this;
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_AFFAIRE_BY_ID_ENDPOINT +
            this.form.affaire_base_id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
        if (response && response.data) {
          _this.selectedModificationAffaire = response.data;

          //Fill values
          this.fillValuesFromModificationAffaire();

          //Expand numéros card
          this.$refs.expandCollapseBtn.$el.click();

          //Search numéros immeubles
          _this.setModificationAffaireNuméros();
        }
        else{
          handleException({msg : "Affaire non trouvée"}, this);
        }
      })
      //Error
      .catch(err => {
        handleException(err, this);
      });
    },

    /**
     * Fill values from modification affaire
     */
    fillValuesFromModificationAffaire(){
      if(this.selectedModificationAffaire){
        this.form.cadastre = this.cadastres_list.filter(x => x.id === this.selectedModificationAffaire.cadastre_id)[0];
        this.form.nom = this.selectedModificationAffaire.nom;
        this.form.nom_ = this.selectedModificationAffaire.nom; // garder le nom pas modifié en mémoire
        this.form.vref = this.selectedModificationAffaire.vref;
        this.form.client_commande = this.clients_list.filter(x => x.id === this.selectedModificationAffaire.client_commande_id)[0];
        this.form.client_commande_complement = this.selectedModificationAffaire.client_commande_complement;
        this.form.client_envoi = this.clients_list.filter(x => x.id === this.selectedModificationAffaire.client_envoi_id)[0];
        this.form.client_envoi_complement = this.selectedModificationAffaire.client_envoi_complement;
        this.form.date_ouverture =  moment(new Date()).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
        this.form.localisation_E = this.selectedModificationAffaire.localisation_e;
        this.form.localisation_N = this.selectedModificationAffaire.localisation_n;

        //Handle localisation
        if(this.selectedModificationAffaire.localisation_e && this.selectedModificationAffaire.localisation_n)
          this.handleLocalisation(this.selectedModificationAffaire.localisation_e, this.selectedModificationAffaire.localisation_n, true);
      }
    },

    /**
     * On select type modif update nom_affaire
     */
    typeModifSelected() {
      this.form.nom = (this.form.affaire_modif_type.id?
                       this.typesModficiationAffaire_list.filter(x => x.id === this.form.affaire_modif_type.id) + " : " : null) + this.form.nom_;
    },

    /**
     * Récupère les numéros référencés, réservés et le client de la facture
     */
    setModificationAffaireNuméros() {
      this.$http
      .get(
        process.env.VUE_APP_API_URL +
          process.env.VUE_APP_AFFAIRE_NUMEROS_ENDPOINT +
          this.form.affaire_base_id + "?affaire_numero_actif=true",
        {
          withCredentials: true,
          headers: { Accept: "application/json" }
        }
      )
      .then(response => {
        if (response && response.data) {
          this.affaire_numeros_all = response.data;
          this.affaire_numeros_nouveaux = response.data.filter(
            x => x.affaire_numero_type_id === Number(process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_NOUVEAU_ID)
          );
          this.affaire_numeros_anciens = response.data.filter(
            x => x.affaire_numero_type_id === Number(process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_ANCIEN_ID)
          );
          this.affaire_numeros_nouveaux.forEach(function(element) {
            if (element.numero_etat_id === Number(process.env.VUE_APP_NUMERO_ABANDONNE_ID)) {
              element.active = false;
            } else {
              element.active = true;
            }
          });

          // get client_affaire
          const url = process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_FACTURES_ENDPOINT + this.form.affaire_base_id;
          this.$http.get(url,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }).then(response => {
            if(response && response.data)
              var affaire_factures = response.data;
              this.client_facture = this.clients_list.filter(x => x.id === affaire_factures[0].client_id)[0];
          }).catch(err => handleException(err, this));
        }
      })
      .catch(err => {
        handleException(err, this);
      });
    },

    /**
     * Récupérer la sélection des anciens numéros
     */
    onSelectNumsAnciens(items) {
      this.selectedAnciensNumeros = items;
    },

    /**
     * Récupérer la sélection des nouveaux numéros
     */
    onSelectNumsNouveux(items) {
      this.selectedNouveauxNumeros = items;
    },

    /**
     * Affiche le complément client si le client est une entreprise
     */
    showClientComplement(client) {
      if (client && client.id) {
        let tmp = this.clients_liste_type.filter(x => x.id === client.id).pop();
        if (tmp.type_id === this.clients_types_config.personne_morale) {
          return true;
        }
      }
      return false;
    },

    /**
     * Init liste of people working in an entreprise
     */
    async initClientMoralPersonnes(client_id, client_type) {
      return new Promise((resolve) => {
        if (client_id) {
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
              let tmp = [];
              response.data.forEach(x => tmp.push([x.titre, x.nom, x.prenom].filter(Boolean).join(" ")));
              this.client_moral_personnes[client_type] = tmp;
              resolve(tmp);
            }
          }).catch(err => this.handleException(err, this));
        }
      });
    },

    /**
     * open create contact
     */
    openCreateContact(client_id) {
      let routeData = this.$router.resolve({name: "ClientsEdit", params: {id: client_id}});
      window.open(routeData.href, "_blank");
    },

    /**
     * Update contact when 
     */
    async updateContact() {
      if (this.form.client_commande !== null && this.form.client_commande.id !== null) {
        this.initClientMoralPersonnes(this.form.client_commande.id, 'commande');
      }
      if (this.form.client_envoi !== null && this.form.client_envoi.id !== null) {
        this.initClientMoralPersonnes(this.form.client_envoi.id, 'envoi');
      }
      if (this.client_facture !== null && this.client_facture.id !== null) {
        this.initClientMoralPersonnes(this.client_facture.id, 'facture');
      }
    }
  },

  mounted: function() {
    //Init search SITN categories
    this.sitn_search_categories = JSON.parse(
      process.env.VUE_APP_SITN_SEARCH_CATEGORIES_ALIASES
    );
    //Init map component
    this.callInitMap();
    //Init lists
    this.initTypesAffairesList();
    this.initClientsList();
    this.initOperateursList();
    this.initCadastresList();
    this.initTypesModficiationAffaire();
  }
};
</script>
