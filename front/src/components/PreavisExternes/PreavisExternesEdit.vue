<style src="./preavisExternesEdit.css"></style>
<template src="./preavisExternesEdit.html"></template>


<script>
import MapHandler from "@/components/MapHandler/MapHandler.vue";
import PreavisEditComments from "@/components/PreavisExternes/PreavisExternesEditComments.vue";
import PreavisEditDecision from "@/components/PreavisExternes/PreavisExternesEditDecision.vue";

import { handleException } from "@/services/exceptionsHandler";

import { Drag, Drop } from 'vue-drag-drop';

import "ol/ol.css";
import {defaults as defaultInteractions, Snap, Modify, MouseWheelZoom} from 'ol/interaction';
import Map from "ol/Map";
import View from "ol/View";
import TileLayer from "ol/layer/Tile";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import {WMTSCapabilities} from "ol/format";
import WMTS from "ol/source/WMTS";
import {optionsFromCapabilities} from "ol/source/WMTS";
import proj4 from "proj4";
import {register as proj_register} from "ol/proj/proj4";
import {Projection} from "ol/proj";
import { Style, Circle, Fill, Stroke, RegularShape } from "ol/style";
import GeoJSON from 'ol/format/GeoJSON';
import {platformModifierKeyOnly} from 'ol/events/condition';

export default {
  name: "PreavisAffaire",
  props: {},
  components: {
    Drag,
    Drop,
    MapHandler,
    PreavisEditComments,
    PreavisEditDecision,
  },
  data() {
    return {
      affaire: {},
      affaireLoaded: false,
      documents: [{}],
      droppedFiles: [],
      mapLoaded: false,
      affaire_data: {},
      map: null,
      center: { x: null, y: null },
      view: null,
      vectorLayer: null,
      vectorSource: null,
      graphicsLayer: null,
      graphicsLayerSource: null,
      markerStyle: null,
      preavisDecisionReady: false,
      service_edition_allowed: false,
      preavisList: [],
    };
  },

  methods: {
    /*
     * SEARCH AFFAIRE PREAVIS
     */
    async getAffaire() {
      return new Promise((resolve, reject) => {
        this.$http.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_PREAVIS_AFFAIRE_BY_ID_ENDPOINT + "?preavis_id=" + this.$route.params.id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        ).then(response => {
          if (response && response.data) {
            this.affaire = response.data;
            resolve(response.data);
            this.affaireLoaded = true;
            this.service_edition_allowed = (response.data.preavis_service_id === Number(JSON.parse(localStorage.getItem("infolica_user")).service_id));
          }
        })
        .catch((err) => {
          handleException(err, this);
          reject(err);
        });
      })
    },

    /**
     * Documents
     */
    async getDocuments() {
      this.$http.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_PREAVIS_DOCUMENTS_BY_AFFAIRE_ID_ENDPOINT + "?affaire_id=" + this.affaire.id,
        {
          withCredentials: true,
          headers: { Accept: "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.documents = response.data;
        }
      }).catch(err => handleException(err));
    },

    /**
     * Open Theme SITN
     */
    openSitnTheme(theme) {
      let route;
      if (theme === "amenagement_territoire") {
            route = process.env.VUE_APP_SITN_AMENAGEMENT_TERRITOIRE_URL;
      } else if (theme === "cadastre") {
            route = process.env.VUE_APP_SITN_CADASTRE_URL;
      } else if (theme === "sites_pollues") {
            route = process.env.VUE_APP_SITN_SITES_POLLUES_URL;
      } else {
          return null;
      }
      window.open(route + "&map_x=" + this.affaire.coord_e + "&map_y=" + this.affaire.coord_n, "_blank");
    },

    /**
     * Download file from table
     */
    async downloadFile(item) {
      let requestParams = [
        'affaire_id=' + this.affaire.id,
        'relpath=' + item.rel_path,
        'filename=' + item.filename,
        '&time=' + new Date().getTime()
      ].join("&");

      window.open(process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_DOWNLOAD_DOCUMENT_ENDPOINT + '?' + requestParams)
    },

    // handleDrop
    handleDrop(data, event) {
      event.preventDefault();
      this.droppedFiles.push(...event.dataTransfer.files);
    },

    // save files on back-end
    async saveFiles() {
      let formData = new FormData();
      formData.append('affaire_id', this.affaire.id);

      for( let i = 0; i < this.droppedFiles.length; i++ ){
        formData.append('files[' + i + ']', this.droppedFiles[i]);
      }

      this.$http.post(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_PREAVIS_POST_FILE_BY_AFFAIRE_ID_ENDPOINT,
        formData,
        {
          withCredentials: true,
          headers: {
            'Accept': "application/json",
            'Content-Type': 'multipart/form-data'
          }
        }
      ).then(() => {
        this.getDocuments();
        this.droppedFiles = [];
      })
      .catch(err => handleException(err, this));
    },

    // remove item from fileupload list
    removeItem(item) {
      let index = this.droppedFiles.indexOf(item);
      if (index !== -1) {
        this.droppedFiles.splice(index, 1);
      }
    },

    // save preavis devinitively and submit it to SGRF
    async savePreavisDefinitively() {
      let ped = this.$refs.ped;
      if (ped.decision.show === true) {
        ped.saveDecision(true).then(() => {
          this.$router.push({name: 'Preavis'});
        }).catch(err => handleException(err));
      } else {
        this.$router.push({name: 'Preavis'});
      }
    },

    /**
     * Init map
     */
    initMap: function(center, zoom) {

      this._crs = process.env.VUE_APP_MAP_PROJECTION;
      proj4.defs(this._crs,
       '+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333'
       + ' +k_0=1 +x_0=2600000 +y_0=1200000 +ellps=bessel '
       + '+towgs84=674.374,15.056,405.346,0,0,0,0 +units=m +no_defs');
      const _extent = [2420000, 1030000, 2900000, 1360000];
      proj_register(proj4);

      //Init marker style
      this.initMarkerStyle();

      // Init GeoJSON reader
      this.geojsonFormat = new GeoJSON();

      // WMTS
      this.wmtsLayer = new TileLayer();

      // Vector layer
      this.vectorSource = new VectorSource();
      this.vectorLayer = new VectorLayer({
        source: this.vectorSource
      });

      this.initWmtsSource();

      // Graphics layer
      this.initGraphicsLayer();

      // Map layers
      const layers = [this.wmtsLayer, this.vectorLayer, this.graphicsLayer];


      const _projection = new Projection({
        code: this._crs,
        extent: _extent,
      });

      this.view = new View({
        projection: _projection,
        center: center
          ? [center.x, center.y]
          : process.env.VUE_APP_MAP_DEFAULT_CENTER,
        zoom: zoom,
        minZoom: 0,
        maxZoom: 17
        });
      if (!this.map) {

        const interactions = new defaultInteractions({
          altShiftDragRotate: false,
          pinchRotate: false,
          mouseWheelZoom: false
        });

        this.map = new Map({
          layers: layers,
          target: document.getElementById("mapDiv"),
          view: this.view,
          interactions: interactions
        });

        let mouseWheelInt = new MouseWheelZoom();
        this.map.addInteraction(mouseWheelInt);

        this.map.on('wheel', function(evt) {
          mouseWheelInt.setActive(platformModifierKeyOnly(evt));
        });

        this.modify = new Modify({
          source: this.vectorSource
        });

        this.snap = new Snap({
          source: this.vectorSource
        });

      } else {
        this.map
          .getView()
          .setCenter(
            center
              ? [center.x, center.y]
              : process.env.VUE_APP_MAP_DEFAULT_CENTER
          );
      }
    },

    /**
     * Init marker style
     */
    initMarkerStyle: function() {
      this.markerStyle = new Style({
        image: new Circle({
          radius: 7,
          fill: new Fill({ color: "yellow" }),
          stroke: new Stroke({
            color: [0, 0, 0],
            width: 2
          })
        })
      });
    },

    /**
     * Init graphics layer
     */
    initGraphicsLayer: function(){
      this.graphicsLayerSource = new VectorSource();
      this.graphicsLayer = new VectorLayer({
        source: this.graphicsLayerSource,
        style: new Style({
          fill: new Fill({ color: '#b3ffff' }),
          stroke: new Stroke({ color: 'red', width: 8 }),
          image: new RegularShape({
            fill: new Fill({ color: 'yellow' }),
            stroke: new Stroke({ color: 'red', width: 4 }),
            points: 4,
            radius: 10,
            radius2: 0,
            angle: Math.PI / 4,
          }),
        }),
        opacity: 0.5
      });
    },

    initWmtsSource: function() {
      this.$http
          .get(
            process.env.VUE_APP_WMTS_GETCAPABILITIES_URL
          )
          .then(response => {
            const parser = new WMTSCapabilities();
            const result = parser.read(response.data);
            const WMTSoptions = optionsFromCapabilities(
              result,{
                layer: process.env.VUE_APP_WMTS_LAYER,
                matrixSet: this._crs
              }
            )
            const source = new WMTS(WMTSoptions);
            this.wmtsLayer.setSource(source);
         });

    },

    /**
     * Add marker
     */
    addMarker: function(x, y, zoom) {
      this.vectorSource.clear();
      const marker = new Feature({
        geometry: new Point([x, y])
      });
      marker.setStyle(this.markerStyle);
      this.vectorSource.addFeature(marker);

      if(zoom){
        this.view.setCenter([x, y]);
        this.view.setZoom(process.env.VUE_APP_MAP_DEFAULT_AFFAIRE_ZOOM);
      }
    },

    /** GET PREAVIS OTHER SERVICES */
    async getOtherPreavis() {
      this.$http.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_SERVICE_EXTERNE_AFFAIRE_PREAVIS_TOUS_ENDPOINT + "?affaire_id=" + this.affaire.id + "&preavis_id=" + this.$route.params.id,
        {
          withCredentials: true,
          headers: { Accept: "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.preavisList = response.data.filter(x => x.id !== Number(this.$route.params.id));
        }
      }).catch(err => handleException(err));
    }



  },

  mounted: function() {
    this.getAffaire().then(() => {
      this.getDocuments();
      this.getOtherPreavis();

      // map
      let center = {x: this.affaire.coord_e, y: this.affaire.coord_n}
      this.initMap(center, process.env.VUE_APP_MAP_DEFAULT_AFFAIRE_ZOOM);
      this.addMarker(center.x, center.y);

      this.$root.$on('setPreavisDecisionDraft', () => {this.preavisDecisionReady = true})
    });
  }
};
</script>
