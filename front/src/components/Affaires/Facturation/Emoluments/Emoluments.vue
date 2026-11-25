<style src="./emoluments.css"></style>
<template src="./emoluments.html"></template>


<script>
import { handleException } from '@/services/exceptionsHandler';
// import { logAffaireEtape } from '@/services/helper';
const numeral = require("numeral");
const moment = require('moment');

export default {
  name: 'Emoluments',
  props: {
    affaire: { type: Object },
    affaire_factures: { type: Array },
    configFactureTypeID: { type: Object },
    factureTypes: { type: Array },
    numeros_references: { type: Array },
    permission: { type: Object },
    typesAffaires_conf: { type: Object },
  },
  data: function () {
    return {
      cadastrationFactureNumerosId_old: [],
      confirmationRemoveDialog: {
        title: "Demande de confirmation",
        msg: "Confirmez-vous la suppression de l'émolument?",
        confirmBtn: "Confirmer",
        cancelBtn: "Annuler",
        show: false,
        onConfirm: () => { },
        onCancel: () => { },
      },
      disabled: false,
      emolument_facture_repartition_ctrl: false,
      emolumentsGeneral_list: [],
      facture_parametres: {
        indice_application: null,
        tva_pc: null,
      },
      factures_repartition: [],
      form_general: {}, //général
      showEmolumentsDialog: false,
      showProgressBar: false,
      total: {
        montant_recapitulatif_mandat: 0,
        montant_recapitulatif_somme1: 0,
        montant_recapitulatif_terrain_materialisation_deplacements: 0,
        montant_recapitulatif_somme2: 0,
        montant_recapitulatif_bureau: 0,
        montant_recapitulatif_somme3: 0,
        montant_recapitulatif_indice_application: 0,
        montant_recapitulatif_somme4: 0,
        montant_recapitulatif_materiel_divers: 0,
        montant_recapitulatif_somme5: 0,
        montant_recapitulatif_matdiff: 0,
        montant_recapitulatif_somme6: 0,
        montant_recapitulatif_tva: 0,
        montant_recapitulatif_somme7: 0,
        montant_recapitulatif_registre_foncier: 0,
        montant_recapitulatif_total: 0,
      },
      tableauEmolumentsNew: [],
      isPageReady: false,
      id_matdiff: process.env.VUE_APP_TABLEAUEMOLUMENTS_MATDIFF_ID.split(',').map(Number),
      divers_tarif_horaire: [],
      divers_tarif_horaire_unit: {
        nom: null,
        nombre: 1,
        montant: null,
        prix: 0,
      },
      selectedHighlightRow: null,
      numeros: [],
      numeros_selection: [],
    }
  },

  methods: {

    /**
     * update emolument_affaire used
     */
    updateUsed() {
      this.fixEmolumentDefinitively(this.form_general.id, this.form_general.utilise);
      this.disabled = this.form_general.utilise;
    },


    // ================================================================================================================================================
    // ================================================================================================================================================
    //                  NEW EMOLUMENTS
    // ================================================================================================================================================
    // ================================================================================================================================================


    // ================================================================================================================================================
    // EMOLUMENT DIALOG
    // ================================================================================================================================================
    async openEmolumentDialog(emolument_affaire_id) {
      await this.getEmolument(emolument_affaire_id);
      await this.getEmolumentAffaireRepartition(emolument_affaire_id).then(response => {
        if (response && response.data) {
          this.initFactureRepartition(response.data);
          this.updateFactureRepartition();
        }
      }).catch(err => handleException(err, this));

      this.numeros.sort((a, b) => a.emolument_affaire_id === emolument_affaire_id? -1: b.emolument_affaire_id === emolument_affaire_id? 1: a.emolument_affaire_id - b.emolument_affaire_id);

      this.showEmolumentsDialog = true;
    },

    /**
     * Cancel formular edition
     */
    async onCancel() {
      await this.getEmolumentsGeneral();
      this.showEmolumentsDialog = false;
    },


    async initForm(form_general = true) {

      if (form_general) {
        this.form_general = {
          id: null,
          affaire_id: this.affaire.id,
          pente_pc: 0,
          diff_visibilite_pc: 0,
          trafic_pc: 0,
          zi: 1,
          nb_batiments: 0,
          indice_application: this.facture_parametres.indice_application,
          tva_pc: this.facture_parametres.tva_pc, // %
          remarque: "",
          facture_type_id: 1,
          numeros: [],
          numeros_id: [],
          utilise: false,

          // Bâtiments
          batiment_f: [],

        };

        this.numeros_selection = [];

        this.divers_tarif_horaire = [];
        this.divers_tarif_horaire.push(JSON.parse(JSON.stringify(this.divers_tarif_horaire_unit)));

        this.disabled = false;

        return await this.getTableauEmolumentsNew();
      }
    },


    // ================================================================================================================================================
    // HANDLE BATIMENTS IN EMOLUMENTS
    // ================================================================================================================================================
    /**
     * Add batiment
     */
    addBatiment() {
      this.form_general.nb_batiments += 1;

      this.tableauEmolumentsNew.forEach(cat => {
        cat.forEach(scat => {
          scat.forEach(pos => {
            pos.nombre.push(0);
            pos.prix.push(0);
          })
        })
      });
    },

    /**
    * Remove batiment
    */
    removeBatiment(batiment_i) {
      let tmp = JSON.parse(JSON.stringify(this.tableauEmolumentsNew));
      tmp.forEach(cat => {
        cat.forEach(scat => {
          scat.forEach(pos => {
            pos.nombre.splice(batiment_i, 1);
            pos.prix.splice(batiment_i, 1);
          })
        })
      })

      this.tableauEmolumentsNew = tmp;

      this.form_general.batiment_f.splice(batiment_i - 1, 1);
      this.form_general.nb_batiments -= 1;

      this.update_sommesPartielles();
    },


    /**
     * Update batimentCorrectionFactor
    */
    updateBatimentCorrectionFactor(idx) {
      let tmp = JSON.parse(JSON.stringify(this.tableauEmolumentsNew));
      tmp.forEach(cat => {
        cat.forEach(scat => {
          scat.forEach(pos => {
            this.updateMontant(pos, idx);
          })
        })
      });
      this.tableauEmolumentsNew = tmp;

      this.update_sommesPartielles();
    },

    // ================================================================================================================================================
    // EMOLUMENTS + EMOLUMENT_AFFAIRE
    // ================================================================================================================================================

    /**
     * Get emoluments affaire - general
     */
    async getEmolumentsGeneral() {
      this.$http.get(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_EMOLUMENT_AFFAIRE_ENDPOINT + "?affaire_id=" + this.affaire.id,
        {
          withCredentials: true,
          headers: { "Accept": "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.initForm();

          this.emolumentsGeneral_list = new Array(response.data.lenght);
          for (let j = 0; j < response.data.length; j++) {
            this.emolumentsGeneral_list[j] = JSON.parse(JSON.stringify(this.form_general));
          }
          for (const [i, form_gen_i] of response.data.entries()) {
            // Parcourir les form_gen

            for (const key in this.form_general) {
              // Set parameters

              if (key in form_gen_i) {
                this.emolumentsGeneral_list[i][key] = form_gen_i[key];
              }
            }
          }
          this.initForm(false); // ddd
          return
        }
      }).catch(err => handleException(err, this));
    },


    /**
     * post
     */
    async postEmolument() {
      this.showProgressBar = true;

      let formData = new FormData();
      formData.append('form_general', JSON.stringify(this.form_general));
      formData.append('emoluments', JSON.stringify(this.tableauEmolumentsNew));
      formData.append('divers_tarifhoraire', JSON.stringify(this.divers_tarif_horaire));

      return new Promise((resolve, reject) => {
        this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_EMOLUMENT_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: { "Accept": "application/json" }
          }
        ).then((response) => {
          if (response && response.data) {
            this.form_general.id = response.data.emolument_affaire_id;
            this.$root.$emit("ShowMessage", "L'émolument a bien été enregistré");
            resolve(response);
          }
        })
          .catch(err => {
            handleException(err, this);
            reject(err);
          })
          .finally(() => this.showProgressBar = false);
      });
    },

    /**
     * fix emolument definitively
     */
    async fixEmolumentDefinitively(emolument_affaire_id, status = true) {
      let formData = new FormData();
      formData.append("emolument_affaire_id", emolument_affaire_id);
      formData.append("utilise", status);

      this.$http.put(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_EMOLUMENT_AFFAIRE_FREEZE_ENDPOINT,
        formData,
        {
          withCredentials: true,
          headers: { "Accept": "application/json" }
        }
      ).then(() => { })
        .catch(err => handleException(err, this));
    },


    /**
     * Get facture parametres
     */
    async getFactureParametres() {
      this.$http.get(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_FACTURE_PARAMETRES_ENDPOINT,
        {
          withCredentials: true,
          headers: { "Accept": "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.facture_parametres = response.data.facture_parametres;
          this.isPageReady = true;
        }
      })
        .catch(err => handleException(err, this));
    },

    /**
     * Get empty table of emoluments
     */
    async getTableauEmolumentsNew() {
      return this.$http.get(
        process.env.VUE_APP_API_URL + "/tableau_emoluments_new?affaire_id=" + this.affaire.id,
        {
          withCredentials: true,
          headers: { "Accept": "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.numeros = response.data.numeros;
          let tmp = response.data.emoluments;
          tmp.forEach(cat => {
            cat.forEach(scat => {
              scat.forEach(pos => {
                pos.prix = [0];
                pos.nombre = [0];
              })
            })
          });

          this.tableauEmolumentsNew = tmp;

        }
      })
        .catch(err => handleException(err, this));
    },

    /**
     * Get emoluments
     */
    async getEmolument(emolument_affaire_id) {
      return this.$http.get(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_EMOLUMENT_ENDPOINT + '?emolument_affaire_id=' + emolument_affaire_id,
        {
          withCredentials: true,
          headers: { "Accept": "application/json" }
        }
      ).then(response => {
        if (response && response.data) {

          this.form_general = JSON.parse(response.data.form_general);
          this.tableauEmolumentsNew = JSON.parse(response.data.emoluments);
          this.divers_tarif_horaire = JSON.parse(response.data.divers_tarifhoraire);
          this.numeros = JSON.parse(response.data.numeros);

          this.numeros_selection = this.numeros.filter(x => x.emolument_affaire_id === this.form_general.id);

          this.disabled = this.form_general.utilise;

          this.initFactureRepartition(response.data);
          this.updateFactureRepartition();

          this.update_sommesPartielles();
        }
      })
        .catch(err => handleException(err, this));
    },

    confirmDelete(emolument_affaire_id) {
      this.confirmationRemoveDialog = {
        title: "Demande de confirmation",
        msg: "Confirmez-vous la suppression de l'émolument?",
        confirmBtn: "Confirmer",
        cancelBtn: "Annuler",
        show: true,
        onConfirm: () => this.deleteEmolument(emolument_affaire_id),
        onCancel: () => { },
      }
    },

    async deleteEmolument(emolument_affaire_id) {
      return this.$http.delete(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_EMOLUMENT_ENDPOINT + '?emolument_affaire_id=' + emolument_affaire_id,
        {
          withCredentials: true,
          headers: { "Accept": "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.getEmolumentsGeneral();
          this.$root.$emit("searchAffaireFactures");
          this.showEmolumentsDialog = false;
        }
      })
        .catch(err => handleException(err, this));
    },

    async handleUpdateEmolument(position, idx) {
      this.updateMontant(position, idx);
      await this.automaticUpdateNombres(position);
      this.update_sommesPartielles();
      return;
    },

    // ================================================================================================================================================
    // HANDLE FACTURES
    // ================================================================================================================================================
    /**
     * init facture repartition
     */
    initFactureRepartition(emolument_facture_repartition) {
      this.factures_repartition = JSON.parse(JSON.stringify(this.affaire_factures));

      if (emolument_facture_repartition.length > 0) {
        // Il existe une/des relations entre l'émolument et les factures
        this.factures_repartition.forEach(x => {
          x.emolument_repartition = 0;
          emolument_facture_repartition.some(y => {
            if (y.facture_id === x.id) {
              x.emolument_repartition = y.repartition;
            }
          });
        });
      } else {
        // Il n'existe pas encore de relation entre l'émolument et les factures
        if (this.factures_repartition.length === 1) {
          this.factures_repartition[0].emolument_repartition = 100;
        } else {
          this.factures_repartition.forEach(x => {
            x.emolument_repartition = 0;
          });
        }
      }
    },

    /**
     * update facture repartition
     */
    updateFactureRepartition() {
      let somme = 0;
      let somme_ = 100;
      this.factures_repartition.forEach(x => {
        somme += Number(x.emolument_repartition);
      });

      if (Math.abs(somme - 100) >= 0.011) {
        this.emolument_facture_repartition_ctrl = true;
      } else {
        this.emolument_facture_repartition_ctrl = false;
        somme_ = somme
      }

      this.factures_repartition.forEach(x => {
        if (Number(x.emolument_repartition) > 0) {
          x.montant_mo = numeral(this.round((Number(this.total.montant_recapitulatif_somme5) * Number(x.emolument_repartition) / somme_), 0.05)).format("0.00");
          x.montant_mat_diff = numeral(this.round((Number(this.total.montant_recapitulatif_matdiff) * Number(x.emolument_repartition) / somme_), 0.05)).format("0.00");
          x.montant_rf = numeral(this.round((Number(this.total.montant_recapitulatif_registre_foncier) * Number(x.emolument_repartition) / somme_), 0.05)).format("0.00");
          x.montant_tva = numeral(this.round((Number(this.total.montant_recapitulatif_tva) * Number(x.emolument_repartition) / somme_), 0.05)).format("0.00");
          x.montant_total = numeral(this.round((Number(this.total.montant_recapitulatif_total) * Number(x.emolument_repartition) / somme_), 0.05)).format("0.00");
        } else {
          x.montant_mo = numeral(0).format("0.00");
          x.montant_mat_diff = numeral(0).format("0.00");
          x.montant_rf = numeral(0).format("0.00");
          x.montant_tva = numeral(0).format("0.00");
          x.montant_total = numeral(0).format("0.00");
        }
      });
    },

    /**
     * Save factures relative to emolument repartitions
     */
    async saveToFactures() {
      this.postEmolument().then((response) => {
        if (response && response.data) {
          this.form_general.id = response.data.emolument_affaire_id;

          let promises = [];
          this.factures_repartition.forEach(x => {
            if (Number(x.emolument_repartition) > 0) {
              promises.push(this.putFacture(x));
            }
          });

          let successMessage = "La facture a été mise à jour avec succès."
          if (promises.length > 1) {
            successMessage = "Les factures ont été mises à jour avec succès."
          }

          Promise.all(promises).then(() => {
            this.showEmolumentsDialog = false;
            this.postEmolumentAffaireRepartition(this.form_general.id);
            this.fixEmolumentDefinitively(this.form_general.id, true);
            this.$root.$emit("searchAffaireFactures");
            this.$root.$emit("ShowMessage", successMessage);
            this.getEmolumentsGeneral();
          }).catch(err => handleException(err, this));
        }
      });
    },

    /**
     * put facture
     */
    async putFacture(facture_data) {
      return new Promise((resolve, reject) => {
        let montant_tva = this.round(Number(facture_data.montant_mo) * Number(this.form_general.tva_pc) / 100, 0.05) + this.round(Number(facture_data.montant_mat_diff) * Number(this.form_general.tva_pc) / 100, 0.05)
        let montant_total = this.round(Number(facture_data.montant_mo) + Number(facture_data.montant_mat_diff) + Number(facture_data.montant_rf) + Number(montant_tva), 0.05)


        let formData = new FormData();
        formData.append("id", facture_data.id);
        formData.append("date", moment(new Date()).format(process.env.VUE_APP_DATEFORMAT_WS));
        formData.append("montant_mo", facture_data.montant_mo);
        formData.append("montant_mat_diff", facture_data.montant_mat_diff);
        formData.append("montant_rf", facture_data.montant_rf);
        formData.append("montant_tva", montant_tva);
        formData.append("montant_total", montant_total);

        this.$http.put(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_FACTURE_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: { "Accept": "application/json" }
          }
        ).then(response => resolve(response))
          .catch(err => reject(err));
      });
    },


    /**
     * on save emoluments repartitions
     */
    onSaveEmolumentsRepartitions() {
      this.confirmationRemoveDialog.title = "Répartition des émoluments dans les factures";
      this.confirmationRemoveDialog.msg = "En cliquant sur 'CONFIRMER', toutes les factures ayant un coefficient de répartition non nul récupéreront les valeurs de ce tableau<br>(si les factures comportaient d'anciennes valeurs, elles seront écrasées).<br>Les factures avec des coefficients nuls ne sont pas modifiées.";
      this.confirmationRemoveDialog.confirmBtn = "Confirmer";
      this.confirmationRemoveDialog.cancelBtn = "Annuler";
      this.confirmationRemoveDialog.onCancel = () => this.confirmationRemoveDialog.show = false;
      this.confirmationRemoveDialog.onConfirm = () => this.saveToFactures();
      this.confirmationRemoveDialog.show = true;
    },




    // ==================================================================================================
    // EMOLUMENT - FACTURE REPARTITION
    // ==================================================================================================
    /**
     * get emolument_affaire_repartition
     */
    async getEmolumentAffaireRepartition(emolument_affaire_id) {
      return new Promise((resolve, reject) => {
        this.$http.get(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_EMOLUMENT_AFFAIRE_REPARTITION_ENDPOINT + "?emolument_affaire_id=" + emolument_affaire_id,
          {
            withCredentials: true,
            headers: { Accept: "appication/json" }
          }
        ).then(response => resolve(response))
          .catch(err => reject(err));
      });
    },

    /**
     * save emolument_affaire_repartition
     */
    async postEmolumentAffaireRepartition(emolument_affaire_id) {
      let formData = new FormData();
      formData.append("emolument_affaire_id", emolument_affaire_id);
      formData.append("emolument_facture_repartition", JSON.stringify(this.factures_repartition));

      return new Promise((resolve, reject) => {
        this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_EMOLUMENT_AFFAIRE_REPARTITION_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: { Accept: "appication/json" }
          }
        ).then((response) => resolve(response))
          .catch(err => reject(err));
      });
    },

    // ==================================================================================================
    // DOWNLOAD EMOLUMENT AS PDF
    // ==================================================================================================
    /**
     * Download emoluments pdf
     */
    async downloadEmoluments() {
      // tableau emoluments
      let tableau_emoluments_html = JSON.parse(JSON.stringify(document.getElementById("tableau_emoluments").outerHTML));
      let inputs = tableau_emoluments_html.matchAll(/(md-input-)\w+/g);
      let value = 0;
      for (const input of inputs) {
        value = document.getElementById(input[0]).value;
        if (Number(value) === 0) {
          tableau_emoluments_html = tableau_emoluments_html.replaceAll(new RegExp(`<input.*(${input[0]}).*?>`, 'g'), '<div class="alignCenter"></div>');
        } else {
          tableau_emoluments_html = tableau_emoluments_html.replaceAll(new RegExp(`<input.*(${input[0]}).*?>`, 'g'), '<div class="alignCenter">' + value + '</div>');
        }
      }
      // fix display when 'CHF' is located after end of div
      tableau_emoluments_html = tableau_emoluments_html.replaceAll(/<\/div>CHF/g, "CHF</div>");
      tableau_emoluments_html = tableau_emoluments_html.replaceAll('<div class="alignCenter">CHF</div>', '<div class="alignCenter"></div>');
      tableau_emoluments_html = tableau_emoluments_html.replaceAll('Nombre', 'Qté');


      // tableau recapitulatif
      let tableau_recapitulatif_html = JSON.parse(JSON.stringify(document.getElementById("tableau_recapitulatif_form").outerHTML));
      inputs = tableau_recapitulatif_html.matchAll(/(md-input-)\w+/g);
      for (const input of inputs) {
        tableau_recapitulatif_html = tableau_recapitulatif_html.replaceAll(new RegExp(`<input.*(${input[0]}).*?>`, 'g'), '<div class="alignCenter">' + document.getElementById(input[0]).value + '</div>');
      }
      tableau_recapitulatif_html = tableau_recapitulatif_html.replaceAll(/<\/div>%/g, " %</div>");

      let formData = new FormData();
      formData.append('tableau_emoluments_id', this.form_general.id);
      formData.append('affaire_id', this.affaire.id);
      formData.append('tableau_emoluments_html', tableau_emoluments_html);
      formData.append('tableau_recapitulatif_html', tableau_recapitulatif_html);

      this.$http.post(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_EXPORT_EMOLUMENTS_PDF_ENDPOINT,
        formData,
        {
          withCredentials: true,
          headers: { "Accept": "application/json" },
          responseType: "blob"
        }
      ).then((response) => {
        let fileURL = window.URL.createObjectURL(new Blob([response.data]));
        let fileLink = document.createElement('a');

        fileLink.href = fileURL;
        let header_content_type = response.headers['content-type'];
        let filename = undefined;
        for (let item of header_content_type.split(';')) {
          item = item.trim();
          if (item.startsWith('filename=')) {
            filename = item.replace('filename=', '').replaceAll('"', '');
            break
          }
        }
        fileLink.setAttribute('download', filename);
        document.body.appendChild(fileLink);
        fileLink.click();
      }).catch(err => {
        handleException(err, this);
      });
    },


    // ==================================================================================================
    // UTILS
    // ==================================================================================================
    /**
      * Round numbers
      */
    round(num, multiple = 0.1) {
      num = Number(num);
      multiple = Number(multiple);
      return Math.round(num / multiple) * multiple;
    },

    updateMontant(position, idx) {
      let f = 1;
      if (idx > 0) {
        f = Number(this.form_general.batiment_f[idx - 1]);
      }
      position.prix[idx] = this.round(f * Number(position.nombre[idx]) * Number(position.montant), 0.05);
      return;
    },

    async automaticUpdateNombres(current_position) {
      let base = [];
      let base_second = []
      this.tableauEmolumentsNew.forEach(cat => {
        cat.forEach(scat => {
          scat.forEach(pos => {
            if (pos.calcul_auto) {
              base = pos.calcul_auto.split('+');
              base_second.filter(x => x !== pos.id_html);
              if (base.includes(current_position.id_html) || base_second.some(x => base.includes(x))) {
                for (let i = 0; i < this.form_general.nb_batiments + 1; i++) {
                  pos.nombre[i] = this.tableauEmolumentsNew.reduce((partialSum, a) => partialSum + a.reduce((partialSum, a) => partialSum + a.reduce((partialSum, a) => partialSum + (base.includes(a.id_html) ? Number(a.nombre[i]) : 0), 0), 0), 0);
                  base_second.push(pos.id_html);
                  this.updateMontant(pos, i);
                }
              }
            }
          });
        });
      });

      return;
    },


    update_sommesPartielles() {
      //sommes partielles du tableau récapitulatif
      this.total.montant_recapitulatif_mandat = 0;
      this.total.montant_recapitulatif_somme1 = 0;
      this.total.montant_recapitulatif_terrain_materialisation_deplacements = 0;
      this.total.montant_recapitulatif_somme2 = 0;
      this.total.montant_recapitulatif_bureau = 0;
      this.total.montant_recapitulatif_somme3 = 0;
      this.total.montant_recapitulatif_indice_application = 0;
      this.total.montant_recapitulatif_somme4 = 0;
      this.total.montant_recapitulatif_materiel_divers = 0;
      this.total.montant_recapitulatif_somme5 = 0;
      this.total.montant_recapitulatif_matdiff = 0;
      this.total.montant_recapitulatif_somme6 = 0;
      this.total.montant_recapitulatif_tva = 0;
      this.total.montant_recapitulatif_somme7 = 0;
      this.total.montant_recapitulatif_registre_foncier = 0;

      // let pos_cat_scat = ''
      this.tableauEmolumentsNew.forEach(cat => {
        cat.forEach(scat => {
          scat.forEach(pos => {
            // mandat (cat 1)
            if (pos.categorie_id === 1) {
              this.total.montant_recapitulatif_mandat += pos.prix.reduce((partialSum, a) => partialSum + a, 0);
              return;
            }

            // travaux terrain (cat 2 + cat 3.1, 3.2, 3.5)
            if ([2, 5].includes(pos.categorie_id) || (pos.categorie_id === 3 && [1, 2, 5].includes(pos.sous_categorie_id))) {
              this.total.montant_recapitulatif_terrain_materialisation_deplacements += pos.prix.reduce((partialSum, a) => partialSum + a, 0);
              return;
            }

            // travaux bureau (cat 4)
            if (pos.categorie_id === 4) {
              this.total.montant_recapitulatif_bureau += pos.prix.reduce((partialSum, a) => partialSum + a, 0);
              return;
            }

            // matériel (cat 3.3)
            if ((pos.categorie_id === 3 && pos.sous_categorie_id === 3) || pos.categorie_id === 6) {
              this.total.montant_recapitulatif_materiel_divers += pos.prix.reduce((partialSum, a) => partialSum + a, 0);
              return;
            }

            // mat diff (cat 3.4)
            if (pos.categorie_id === 3 && pos.sous_categorie_id === 4) {
              this.total.montant_recapitulatif_matdiff += pos.prix.reduce((partialSum, a) => partialSum + a, 0);
              return;
            }

            // RF (cat 7)
            if (pos.categorie_id === 7) {
              this.total.montant_recapitulatif_registre_foncier += pos.prix.reduce((partialSum, a) => partialSum + a, 0);
              return;
            }

            // pos not used if any ?
            console.error(` ${pos.id} - ${pos.id_html} - ${pos.nom} /!\\  update_sommesPartielles | not used position: pos=`, pos);
          })
        })
      });

      // update total.montant_recapitulatif_matdiff with indice_application
      this.total.montant_recapitulatif_matdiff = this.round(this.total.montant_recapitulatif_matdiff * this.form_general.indice_application, 0.05);

      // add divers_tarif_horaire to corresponding sum
      this.total.montant_recapitulatif_materiel_divers += this.divers_tarif_horaire.reduce((partialSum, a) => partialSum + a.prix, 0);
      this.total.montant_recapitulatif_somme1 = this.total.montant_recapitulatif_mandat;
      this.total.montant_recapitulatif_somme2 = this.total.montant_recapitulatif_somme1 + this.total.montant_recapitulatif_terrain_materialisation_deplacements;
      this.total.montant_recapitulatif_somme3 = this.total.montant_recapitulatif_somme2 + this.total.montant_recapitulatif_bureau;
      this.total.montant_recapitulatif_indice_application = this.round(this.total.montant_recapitulatif_somme3 * (this.form_general.indice_application - 1), 0.05);
      this.total.montant_recapitulatif_somme4 = this.total.montant_recapitulatif_somme3 + this.total.montant_recapitulatif_indice_application;
      this.total.montant_recapitulatif_somme5 = this.total.montant_recapitulatif_somme4 + this.total.montant_recapitulatif_materiel_divers;
      this.total.montant_recapitulatif_somme6 = this.total.montant_recapitulatif_somme5 + this.total.montant_recapitulatif_matdiff;
      this.total.montant_recapitulatif_tva = this.round(this.total.montant_recapitulatif_somme6 * this.form_general.tva_pc / 100, 0.05);
      this.total.montant_recapitulatif_somme7 = this.total.montant_recapitulatif_somme6 + this.total.montant_recapitulatif_tva;
      this.total.montant_recapitulatif_total = this.total.montant_recapitulatif_somme7 + this.total.montant_recapitulatif_registre_foncier;

      return;
    },

    addDivers() {
      this.divers_tarif_horaire.push(JSON.parse(JSON.stringify(this.divers_tarif_horaire_unit)));
    },

    updateMatDiffNumber(position) {
      if (position.id == this.id_matdiff[0]) {
        let tmp = Number(position.nombre[0]);

        let tmp_5 = 0;
        let tmp_10 = 0;
        let tmp_15 = 0;
        let tmp_gt15 = 0;
        let c = 1;
        while (tmp > 0) {
          if (c <= 5) {
            // de 1 à 5 points
            tmp_5 += 1;
          } else if (c <= 10) {
            // de 6 à 10 points
            tmp_10 += 1;
          } else if (c <= 15) {
            // de 11 à 15 points
            tmp_15 += 1;
          } else {
            // plus de 16 points
            tmp_gt15 += 1;
          }

          tmp -= 1;
          c += 1;
        }

        this.tableauEmolumentsNew.forEach(cat => {
          cat.forEach(scat => {
            scat.forEach(pos => {
              if (pos.id === this.id_matdiff[0]) { pos.nombre[0] = tmp_5; this.updateMontant(pos, 0) }
              if (pos.id === this.id_matdiff[1]) { pos.nombre[0] = tmp_10; this.updateMontant(pos, 0) }
              if (pos.id === this.id_matdiff[2]) { pos.nombre[0] = tmp_15; this.updateMontant(pos, 0) }
              if (pos.id === this.id_matdiff[3]) { pos.nombre[0] = tmp_gt15; this.updateMontant(pos, 0) }
            })
          })
        });
      }
    },

    highlithtSelectedRow(position_id) {
      this.selectedHighlightRow = position_id;
    },

    /**
    * on select BF reference (cadastration)
    */
    onSelectBFReferences(items) {
      let numeros_id = [];
      items.forEach(x => numeros_id.push(x.numero_id));

      this.form_general.numeros_id = numeros_id;
    },
  },

  mounted: function () {
    this.getEmolumentsGeneral();
    this.getFactureParametres();

    this.addDivers();

    this.$root.$on("getEmolumentsGeneral", () => this.getEmolumentsGeneral());
  }
}
</script>

