<style src="./notifications.css" scoped></style>
<template src="./notifications.html"></template>


<script>

export default {
  name: 'Notifications',
  data: () => ({
    msg: String,
    showSnackbar: false,
    isError: false
  }),

  mounted: function(){
    //Show Message
    this.$root.$on('ShowMessage', (msg) =>{
      this.msg = msg;
      this.isError = false;
      this.showSnackbar = true;      
    });

    //Show Error
    this.$root.$on('ShowError', (msg) =>{
      this.msg = msg;
      this.isError = true;
      this.showSnackbar = true;      
    });
  }
}
</script>

