<style src="./main.css" scoped></style>
<template src="./main.html"></template>


<script>
import Login from '@/components/Login/Login.vue'


export default {
  name: 'Main',
  components: {
    Login
  },
  data: () => ({
    isAuthenticated: false
  }),
  methods: {
    /**
     * Set default date format in datepicker
     */
    setDefaultDateFormat() {
      this.$material.locale.dateFormat = "dd.MM.yyyy";
      this.$material.locale.firstDayOfAWeek = 1;
    }
  },
  mounted: function(){
    this.setDefaultDateFormat();
  }
}
</script>

