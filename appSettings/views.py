from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Setting

class SettingsView(APIView):
    def get(self, request, format=None):
        settings_dict = {}
        
        try:
            setting_objects = Setting.objects.all()

            for setting in setting_objects:
                settings_dict[setting.name] = setting.value

            return Response(settings_dict, status=200)
        
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
    def post(self, request, format=None):
        # Handle creating a new setting in the database here

        #JSON Object: {"settings":[{"NAME":NAME, "VALUE":VALUE}, {"NAME":NAME, "VALUE":VALUE}]}
        settings = request.data['settings']
        bad_settings = []

        for setting in settings:
            try:
                new_setting = Setting(name=setting['NAME'], value=setting['V'])
                new_setting.save()
            except:
                bad_settings.append(setting)

        if len(bad_settings) > 0:
            return Response({"INVALID SETTINGS": bad_settings}, status=200)
        else:
            return Response({"SUCCESS": "All settings were successfully saved"}, status=200)
        
