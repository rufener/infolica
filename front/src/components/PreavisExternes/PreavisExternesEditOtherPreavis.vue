<style src="./preavisExternesEditOtherPreavis.css" scoped></style>
<template src="./preavisExternesEditOtherPreavis.html"></template>


<script>

import { handleException } from "@/services/exceptionsHandler";

export default {
  name: "preavisExternesEditOtherPreavis",
  props: {
    preavis_id: Number,
    affaire_id: Number,
  },
  components: {},
  data() {
    return {
      preavisList: [],
    };
  },

  methods: {
    /** GET PREAVIS OTHER SERVICES */
    async getOtherPreavis() {
      this.$http.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_SERVICE_EXTERNE_AFFAIRE_PREAVIS_TOUS_ENDPOINT + "?affaire_id=" + this.affaire_id + "&preavis_id=" + this.preavis_id,
        {
          withCredentials: true,
          headers: { Accept: "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.preavisList = response.data.filter(x => x.id !== this.preavis_id);
        }
      }).catch(err => handleException(err));
    }
  },

  mounted: function() {
    this.getOtherPreavis();
  }
};
</script>
