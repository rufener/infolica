<style src="./affairesDashboard.css" scoped></style>
<template src="./affairesDashboard.html"></template>


<script>
import InfosGenerales from "@/components/Affaires/InfosGenerales/InfosGenerales.vue";
import MapHandler from "@/components/MapHandler/MapHandler.vue";
import NumerosAffaire from "@/components/Affaires/NumerosAffaire/NumerosAffaire.vue";
import Documents from "@/components/Affaires/Documents/Documents.vue";
import Suivi from "@/components/Affaires/Suivi/Suivi.vue";
import Preavis from "@/components/Affaires/Preavis/Preavis.vue";
import DuplicationAffaire from "@/components/Affaires/DuplicationAffaire/DuplicationAffaire.vue";
import Facturation from "@/components/Facturation/Facturation.vue";
import Remarques from "@/components/Affaires/Remarques/Remarques.vue";
import ControleMutation from "@/components/Affaires/ControleMutation/ControleMutation.vue";
import ControlePPE from "@/components/Affaires/ControlePPE/ControlePPE.vue";
import SuiviMandat from "@/components/SuiviMandat/SuiviMandat.vue";
import ClotureAffaire from "@/components/Affaires/ClotureAffaire/ClotureAffaire.vue";

import {checkPermission} from '@/services/helper'

import moment from "moment";

export default {
  name: "AffairesDashboard",
  props: {},
  components: {
    InfosGenerales,
    MapHandler,
    NumerosAffaire,
    Documents,
    Suivi,
    Preavis,
    Facturation,
    Remarques,
    ControleMutation,
    ControlePPE,
    SuiviMandat,
    DuplicationAffaire,
    ClotureAffaire
  },
  data() {
    return {
      affaire: {},
      affaireLoaded: false,
      mapLoaded: false,
      editAffaireAllowed: true,
      parentparentAffaireReadOnly: false,
      cloreAffaireEnabled: false,
      duplicationAffaireForm: null,
      typesAffaires: {
        mutation: Number(process.env.VUE_APP_TYPE_AFFAIRE_DIVISION),
        cadastration: Number(process.env.VUE_APP_TYPE_AFFAIRE_CADASTRATION),
        ppe: Number(process.env.VUE_APP_TYPE_AFFAIRE_PPE),
        pcop: Number(process.env.VUE_APP_TYPE_AFFAIRE_PCOP),
        maj_periodique: Number(process.env.VUE_APP_TYPE_AFFAIRE_MAJ_PERIODIQUE),
        modification: Number(process.env.VUE_APP_TYPE_AFFAIRE_MODIFICATION),
        revision_abornement: Number(process.env.VUE_APP_TYPE_AFFAIRE_REVISION_ABORNEMENT),
        remaniement_parcellaire: Number(process.env.VUE_APP_TYPE_AFFAIRE_REMANIEMENT_PARCELLAIRE),
        servitude: Number(process.env.VUE_APP_TYPE_AFFAIRE_SERVITUDE),
        autre: Number(process.env.VUE_APP_TYPE_AFFAIRE_AUTRE)
      }
      // numeros_base_associes = []
    };
  },

  methods: {
    /*
     * SEARCH AFFAIRE
     */
    async searchAffaire() {
      return new Promise((resolve, reject) => {
        this.$http
          .get(
            process.env.VUE_APP_API_URL +
              process.env.VUE_APP_AFFAIRE_BY_ID_ENDPOINT +
              this.$route.params.id,
            {
              withCredentials: true,
              headers: { Accept: "application/json" }
            }
          )
          .then(response => {
            if (response.data) {
              var obj = response.data;

              obj["client_commande_nom_"] = [
                obj.client_commande_entreprise,
                obj.client_commande_complement? obj.client_commande_complement: [obj.client_commande_titre, obj.client_commande_nom, obj.client_commande_prenom].filter(Boolean).join(" "),
                obj.client_commande_co,
                obj.client_commande_adresse,
                obj.client_commande_case_postale,
                [obj.client_commande_npa, obj.client_commande_localite].filter(Boolean).join(" ")]
                .filter(Boolean).join("\n");

              obj["client_envoi_nom_"] = [
                obj.client_envoi_entreprise,
                obj.client_envoi_complement !== null? obj.client_envoi_complement: [obj.client_envoi_titre, obj.client_envoi_nom, obj.client_envoi_prenom].filter(Boolean).join(" "),
                obj.client_envoi_co,
                obj.client_envoi_adresse,
                obj.client_envoi_case_postale,
                [obj.client_envoi_npa, obj.client_envoi_localite].filter(Boolean).join(" ")]
                .filter(Boolean).join("\n");

              obj["technicien"] = [obj.technicien_prenom, obj.technicien_nom]
                .filter(Boolean).join(" ");

              obj["responsable"] = [obj.responsable_prenom, obj.responsable_nom]
                .filter(Boolean).join(" ");

              Object.keys(obj).forEach(function(key) {
                // Formater la date en DD.MM.YYYY
                if (key.includes("date") && obj[key] !== null && obj[key] !== "") {
                  obj[key] = moment(obj[key], process.env.VUE_APP_DATEFORMAT_WS).format(process.env.VUE_APP_DATEFORMAT_CLIENT);
                }
              });
              resolve(obj);
            }
          })
          .catch(() => reject);
      });
    },

    /**
     * Set affaire
     */
    setAffaire() {
      let _this = this;
      this.searchAffaire().then(function(obj){
        _this.affaire = obj;
        _this.affaireLoaded = true;
        _this.editAffaireAllowed = checkPermission(process.env.VUE_APP_AFFAIRE_EDITION);
        _this.cloreAffaireEnabled = (_this.affaire.date_cloture === null || _this.affaire.date_cloture === undefined) && (_this.affaire.date_envoi === null || _this.affaire.date_envoi === undefined);
        _this.parentAffaireReadOnly = (_this.affaire.date_cloture !== null && _this.affaire.date_cloture !== undefined) && (_this.affaire.date_envoi !== null && _this.affaire.date_envoi !== undefined);

        //If admin, allow edit
        if(checkPermission(process.env.VUE_APP_FONCTION_ADMIN)){
          _this.parentAffaireReadOnly = false;
        }

        _this.showMap();
      });


    },

    /**
     * Show map
     */
    showMap() {
      if(this.$refs && this.$refs.mapHandler && !this.mapLoaded){
        this.center = {
          x: this.affaire.localisation_e,
          y: this.affaire.localisation_n
        };
        this.$refs.mapHandler.initMap(
          this.center,
          process.env.VUE_APP_MAP_DEFAULT_AFFAIRE_ZOOM
        );
        this.$refs.mapHandler.addMarker(this.center.x, this.center.y);
        this.$refs.mapHandler.modify.setActive(false);
        this.$refs.mapHandler.snap.setActive(false);
        this.$refs.mapHandler.modify.on("modifyend", this.onFeatureChange(this));
        this.mapLoaded = true;
      }
    },

    onFeatureChange(_this) {

      return function(modify) {
        const features = modify.features.getArray();
        if (features) {
          const feature = features[0];
          const coordinates = feature.getGeometry().getCoordinates();
          _this.affaire.localisation_e = coordinates[0];
          _this.affaire.localisation_n = coordinates[1];
        }
      };
    },

    /**
     * Cloture affaire
     */
    callClotureAffaire() {
      this.$refs.clotureAffaireForm.openClotureDialog();
    },

    /**
     * Duplicate affaire
     */
    duplicateAffaire(){
      this.$refs.duplicationAffaireForm.openDuplicationAffaireDialog();
    },

    /**
     * Open Theme SITN
     */
    openSitnTheme(choix) {
      var route;
      if (choix === "environnement") {
        route = process.env.VUE_APP_SITN_ENVIRONNEMENT_URL;
      } else if (choix === "amenagement_territoire") {
          route = process.env.VUE_APP_SITN_AMENAGEMENT_TERRITOIRE_URL;
      } else {
        return null;
      }
      window.open(route + "&map_x=" + this.affaire.localisation_e + "&map_y=" + this.affaire.localisation_n, "_blank");
    },

    modifyOff(value) {
      if (value === false) {
        this.$refs.mapHandler.modify.setActive(true);
        this.$refs.mapHandler.snap.setActive(true);
      } else {
        this.$refs.mapHandler.modify.setActive(false);
        this.$refs.mapHandler.snap.setActive(false);
        this.$refs.mapHandler.addMarker(this.affaire.localisation_e, this.affaire.localisation_n);
        this.center.x = this.affaire.localisation_e;
        this.center.y = this.affaire.localisation_n;
      }
    }
  },

  mounted: function() {
    this.setAffaire();
    this.$root.$on('mapHandlerReady', () =>{

      this.showMap();
    });
  }
};
</script>
