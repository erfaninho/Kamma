from functools import cached_property
from colorfield.fields import ColorField

from django.db import models
from django_autoutils.model_utils import AbstractModel, upload_file
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from utils.default_string import S, D


class Category (AbstractModel):
    """
        Create Category Model Using Abstract model
    """
    class Genders (models.IntegerChoices):
        FEMALE= 1, "FEMALE"
        MALE= 2,"MALE"
        UNISEX = 3,"UNISEX"
    
    name = models.CharField(_("name"), max_length=255)
    gender = models.IntegerField(choices=Genders.choices)
    colors = ArrayField(models.IntegerField(), blank=True, default=list)
    materials = ArrayField(models.IntegerField(), blank=True, default=list)

    def __str__(self):
        return self.name
    
    def update_attributes (self , color , material):
        self.colors.append(color)
        self.materials.append(material)

        self.save(update_fields=[S.COLORS, S.MATERIALS])

    class Meta:
        db_table = D.CATEGORY
        verbose_name = _("category")
        verbose_name_plural = _("categories")


class ProductAttributes (AbstractModel):
    """
        Class for all of product attributes
    """

    name = models.CharField(_("name"), max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
    

class Color (ProductAttributes):
    """
        Product Color Model
    """
    color = ColorField(_("color"), max_length=10, default="#FFFFFF")

    class Meta:
        db_table = D.COLOR
        verbose_name = _("color")
        verbose_name_plural = _("colors")


class Material (ProductAttributes):
    """
        Product Material Model
    """

    class Meta:
        db_table = D.MATERIAL
        verbose_name = _("material")
        verbose_name_plural = _("materials")


class Size (ProductAttributes):
    """
        Create Item Size Model
    """

    class Meta:
        db_table = D.SIZE
        verbose_name = _("size")
        verbose_name_plural = _("sizes")


class Product (AbstractModel):
    """
        Main Product Model
    """

    name = models.CharField(_("name"), max_length=255)
    category = models.ForeignKey(Category, verbose_name=_("category"), on_delete=models.PROTECT, related_name="products")
    rate = models.FloatField(_("rate"), default=0.0)
    description = models.TextField(_("description"), blank=True, null=True)
    image = models.FileField(upload_to="Products/", max_length=255, null=True, blank=True)
    price = models.PositiveIntegerField(_("price"))
    material =  models.ForeignKey(Material, verbose_name=_("material"), on_delete=models.PROTECT, related_name="products")

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = D.PRODUCT
        verbose_name = _("product")
        verbose_name_plural = _("products")


class ProductInstance (AbstractModel):
    """
        Different Product Instances Model
    """

    product = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.PROTECT, related_name="instances")
    stock = models.PositiveIntegerField(_("stock"))
    color = models.ForeignKey(Color, verbose_name=_("color"), on_delete=models.PROTECT, related_name="instances")
    size = models.ForeignKey(Size, verbose_name=_("size"), on_delete=models.PROTECT, related_name="instances")
    p_id = models.CharField(_("p_id"), max_length=255)

    class Meta:
        db_table = D.PRODUCT_INSTANCES
        verbose_name = _("product_instance")
        verbose_name_plural = _("product_instances")

    def __str__(self):
        return self.p_id
    


class ProductAlbum (AbstractModel):
    """
        Product Album to Store product Medias
    """

    product  = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.CASCADE, related_name="album")
    file = models.FileField(upload_to=upload_file, max_length=255)

    def __str__(self):
        return f"{self.product}:{self.id}"
    
    class Meta:
        db_table = D.ALBUM
        verbose_name = _("album")
        verbose_name_plural = _("albums")


class Comment (AbstractModel):
    """
        Product Comment Class
    """

    #TODO - To be implemented after user model implementation