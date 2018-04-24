from django.db import models

from crim.models.person import CRIMPerson
from crim.models.observation import CRIMObservation


class CRIMRelationship(models.Model):
    class Meta:
        app_label = 'crim'
        verbose_name = 'Relationship'
        verbose_name_plural = 'Relationships'

    relationship_id = models.SlugField(
        'relationship ID',
        max_length=64,
        unique=True,
    )

    observer = models.ForeignKey(
        CRIMPerson,
        on_delete=models.SET_NULL,
        to_field='person_id',
        null=True,
        db_index=True,
        related_name='relationships',
    )

    model_observation = models.ForeignKey(
        CRIMObservation,
        on_delete=models.CASCADE,
        to_field='observation_id',
        db_index=True,
        related_name='observations_as_model',
    )
    derivative_observation = models.ForeignKey(
        CRIMObservation,
        on_delete=models.CASCADE,
        to_field='observation_id',
        db_index=True,
        related_name='observations_as_derivative',
    )
    reverse_direction = models.BooleanField(default=False)

    rt_q = models.BooleanField('quotation', default=False)
    rt_q_exact = models.BooleanField('exact', default=False)
    rt_q_monnayage = models.BooleanField('monnayage', default=False)
    rt_tm = models.BooleanField('mechanical transformation', default=False)
    rt_tm_snd = models.BooleanField('sounding in different voice(s)', default=False)
    rt_tm_minv = models.BooleanField('melodically inverted', default=False)
    rt_tm_retrograde = models.BooleanField('retrograde', default=False)
    rt_tm_ms = models.BooleanField('metrically shifted', default=False)
    rt_tm_transposed = models.BooleanField('transposed', default=False)
    rt_tm_invertible = models.BooleanField('double or invertible counterpoint', default=False)
    rt_tnm = models.BooleanField('non-mechanical transformation', default=False)
    rt_tnm_embellished = models.BooleanField('embellished', default=False)
    rt_tnm_reduced = models.BooleanField('reduced', default=False)
    rt_tnm_amplified = models.BooleanField('amplified', default=False)
    rt_tnm_truncated = models.BooleanField('truncated', default=False)
    rt_tnm_ncs = models.BooleanField('new counter-subject', default=False)
    rt_tnm_ocs = models.BooleanField('old counter-subject shifted', default=False)
    rt_tnm_ocst = models.BooleanField('old counter-subject transposed', default=False)
    rt_tnm_nc = models.BooleanField('new combination', default=False)
    rt_nm = models.BooleanField('new material', default=False)
    rt_om = models.BooleanField('omission', default=False)

    remarks = models.TextField('remarks (supports Markdown)', blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    needs_review = models.BooleanField(default=False)

    def __str__(self):
        return '{0}'.format(self.relationship_id)

    def _get_unique_slug(self):
        slug_base = (self.model_observation.piece.piece_id + '-' +
                     self.derivative_observation.piece.piece_id)
        num = 1
        unique_slug = '{}-{}'.format(slug_base, num)
        while CRIMRelationship.objects.filter(relationship_id=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug_base, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        # Create unique id based on the piece_id of the pieces involved
        if not self.relationship_id:
            self.relationship_id = self._get_unique_slug()
        # Set the parent relationship type field to true if any of the subtypes are
        if self.rt_q_exact or self.rt_q_monnayage:
            self.rt_q = True
        if (self.rt_tm_snd or self.rt_tm_minv or self.rt_tm_retrograde or
                self.rt_tm_ms or self.rt_tm_transposed or self.rt_tm_invertible):
            self.rt_tm = True
        if (self.rt_tnm_embellished or self.rt_tnm_reduced or self.rt_tnm_amplified or
            self.rt_tnm_truncated or self.rt_tnm_ncs or self.rt_tnm_ocs or
                self.rt_tnm_ocst or self.tnm_nc):
            self.rt_tnm = True

        # Finalize changes
        super().save()
