/*global module:false*/
module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    // Metadata.
    meta: {
      version: '0.1.0'
    },
    banner: '/*! PROJECT_NAME - v<%= meta.version %> - ' +
      '<%= grunt.template.today("yyyy-mm-dd") %>\n' +
      '* http://PROJECT_WEBSITE/\n' +
      '* Copyright (c) <%= grunt.template.today("yyyy") %> ' +
      'YOUR_NAME; Licensed MIT */\n',
    // Task configuration.
    shell: {
      multiple: {
        command: [
          'bower install',
          'cd bower_components/bootstrap',
          'npm install',
          'grunt dist --force',
          'cd ../../'
        ].join('&&')
      }
    },
    copy: {
      target: {
        files: [
          {
            expand: true,
            flatten: true,
            src: [
              'bower_components/jquery/dist/jquery.min.js',
              'bower_components/datatables/media/js/jquery.dataTables.min.js'
            ],
            dest: 'campustextbook/assets/vendor/js/'
          },
          {
            expand: true,
            flatten: true,
            src: [
              'bower_components/datatables/media/images/*.png'
            ],
            dest: 'campustextbook/assets/vendor/images/'
          },
          {
            expand: true,
            flatten: true,
            src: [
              'bower_components/bootstrap/dist/css/bootstrap.min.css',
              'bower_components/datatables/media/css/jquery.dataTables.min.css'
            ],
            dest: 'campustextbook/assets/vendor/css/'
          },
          {
            expand: true,
            flatten: true,
            src: [
              'bower_components/bootstrap/dist/fonts/*'
            ],
            dest: 'campustextbook/assets/vendor/fonts/'
          }
        ]
      }
    }
  });

  grunt.loadNpmTasks('grunt-shell');
  grunt.loadNpmTasks('grunt-contrib-copy');

  // Default task.
  grunt.registerTask('default', ['shell', 'copy']);
};
