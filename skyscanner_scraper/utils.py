# 
#  utils.py
#  skyscraper
#  
#  Created by Antonin Lacombe on 2013-05-24.
#  Copyright 2013 Antonin Lacombe. All rights reserved.
# 

def merge_or_create(model, defaults={}, **get_kw):
   """
   returns a triplet:
   instance, created, merged
   """
   instance, created = model.objects.get_or_create(defaults=defaults, **get_kw)
   needs_save = False
   if not created:
      for ppty, value in defaults.items():
         if getattr(instance, ppty) != value:
            setattr(instance, ppty, value)
            needs_save = True
      if needs_save:
         instance.save()
   merged = needs_save
   return instance, created, merged
