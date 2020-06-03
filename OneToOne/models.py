from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class Profile(models.Model):
    """
    A class based model for storing the records of a university student
    Note: A OneToOne relation is established for each student with User model.
    """
    SOURCE_CHOICES = (
        ('Online', 'Online'), ('Referral', ' Referral'), ('Old', 'Old Customer'), ('Phone ', ' Phone Call'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, )
    contactname = models.CharField(max_length=100)
    billingaddress1 = models.TextField(max_length=100)
    installaddress1 = models.TextField(max_length=100)
    billingaddress2 = models.TextField(max_length=100, blank=True, null=True)
    installaddress2 = models.TextField(max_length=100, blank=True, null=True)
    contactno = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True)
    invitationcode = models.CharField(max_length=20, unique=True)
    joindate = models.DateField(null=True, blank=True, auto_now_add=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    comment = models.TextField(max_length=300, blank=True, null=True)
    isconfirm = models.BooleanField(default=False)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class EmailVerification(models.Model):
    code_of_verification = models.CharField(max_length=254, unique=True)
    username = models.CharField(max_length=100, primary_key=True)
    date = models.DateTimeField(auto_now=True)


# hadhci jdid dalchi dyal l machine wl case wl filter ....

class MainPack(models.Model):
    packagecode = models.CharField(max_length=30, unique=True)
    isbytime = models.BooleanField(default=True)
    isbyusage = models.BooleanField(default=False)
    price = models.FloatField()
    exfiltermonth = models.IntegerField(default=6)
    exfiltervolume = models.IntegerField(default=2500)
    packagedetail = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.packagecode


class Machine(models.Model):
    PRODUCT_CHOICES = (('WPU', 'Water Purifier'), ('U', 'Under Sink'), ('F', 'Filter'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    machineid = models.CharField(max_length=100, unique=True)
    installaddress1 = models.TextField(max_length=100)
    installaddress2 = models.TextField(max_length=300, blank=True)
    photoncode = models.CharField(max_length=100)
    mac = models.CharField(max_length=100, blank=True)
    main_pack = models.ForeignKey(MainPack, on_delete=models.CASCADE)
    installdate = models.DateField(null=True, blank=True, auto_now_add=True)
    nextservicedate = models.DateField(null=True, blank=True)
    producttype = models.CharField(max_length=3, choices=PRODUCT_CHOICES)
    price = models.FloatField()

    def __str__(self):
        return "%s %s " % (self.machineid, self.machinetype)

    def get_period(self):
        return "%s " % self.maintenance.exfiltermonth


class Filter(models.Model):
    filtercode = models.CharField(max_length=30,unique=True)
    filtername = models.CharField(max_length=30)
    filterdetail = models.CharField(max_length=300)
    price = models.FloatField()

    def __str__(self):
        return self.filtername


class Technician(models.Model):
    staffcode = models.CharField(max_length=30, unique=True)
    staffshort = models.CharField(max_length=5, default='')
    staffname = models.CharField(max_length=30)
    staffcontact = models.CharField(max_length=300)
    email = models.EmailField(max_length=30)

    def __str__(self):
        return self.staffshort



class Case(models.Model):
    CASE_TYPE = [('Filter replacement', 'Filter replacement'), ('Urgent Repair', 'Urgent Repair'),
                 ('Installation', 'Installation'), ('Checking', 'Checking')]
    machines = models.ManyToManyField(Machine)
    casetype = models.CharField(max_length=100, choices=CASE_TYPE)
    scheduledate = models.DateField(null=True, blank=False)
    time = models.TimeField(null=True, blank=False)
    action = models.TextField(max_length=100, blank=True)
    suggest = models.TextField(max_length=100, blank=True)
    comment = models.TextField(max_length=100, blank=True)
    iscompleted = models.BooleanField(default=False, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filters = models.ManyToManyField(Filter, blank=True)
    handledby = models.ForeignKey(Technician, on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s " % (self.casetype, self.customer.username)

    #def get_absolute_url(self):
    #    return reverse("crm:caselist")

    def get_machine(self):
        return ",".join([str(p) for p in self.machine.all()])

    def get_filter(self):
        return " / ".join([str(f) for f in self.filter.all()])