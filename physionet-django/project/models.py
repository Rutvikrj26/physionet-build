import os

from ckeditor.fields import RichTextField
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from physionet.settings import MEDIA_ROOT
from .utility import get_tree_size

import pdb

def new_creation(receiver_function):
    """
    Decorator for a receiver function to only trigger upon model
    creation from non-fixtures.
    """
    def func_wrapper(*args, **kwargs):
        #pdb.set_trace()
        if kwargs.get('created') and not kwargs.get('raw'):
            return receiver_function(*args, **kwargs)

    return func_wrapper


class Affiliation(models.Model):
    """
    Affiliations belonging to an author or collaborator

    """
    name = models.CharField(max_length=255)

    # member_object points to a Creator or Contributor.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    member_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('name', 'content_type', 'object_id'))


class Member(models.Model):
    """
    Inherited by the Author and Contributor classes.

    """
    # The member will point to a project OR published project
    project = models.ForeignKey('project.Project', related_name='%(class)ss',
        null=True, blank=True)
    published_project =models.ForeignKey('project.PublishedProject',
        related_name='%(class)s', null=True, blank=True)

    first_name = models.CharField(max_length=100, default='')
    middle_names = models.CharField(max_length=200, default='', blank=True)
    last_name = models.CharField(max_length=100, default='')
    is_human = models.BooleanField(default=True)
    organization_name = models.CharField(max_length=200, default='')
    display_order = models.SmallIntegerField()
    affiliations = GenericRelation(Affiliation)

    def __str__(self):
        if self.is_human:
            name = self.user.email
        else:
            name = self.organization_name
        return '%s at %s' % (name, self.project)

    class Meta:
        abstract = True

    def get_full_name(self):
        if self.middle_names:
            return ' '.join([self.first_name, self.middle_names,
                           self.last_name])
        else:
            return ' '.join([self.first_name, self.last_name])


class AuthorManager(models.Manager):
    def get_by_natural_key(self, user, project):
        return self.get(user=user, project=project)


class Author(Member):
    """
    A project's author/creator (datacite). Credited for creating the
    resource.

    Datacite definition:
        "The main researchers involved
        in producing the data, or the
        authors of the publication, in
        priority order."

    """
    class Meta:
        unique_together = (('user', 'project'), ('user', 'published_project'))

    def natural_key(self):
        return (self.user, self.project)

    objects = AuthorManager()

    # Authors must have physionet profiles, unless they are organizations.
    user = models.ForeignKey('user.User', related_name='authorships',
        blank=True, null=True)

@receiver(post_save, sender=Author)
@new_creation
def setup_author(sender, **kwargs):
    """
    When an Author is created:
    - Import profile names.
    """
    pdb.set_trace()
    author = kwargs['instance']
    if author.is_human:
        profile = author.user.profile
        for field in ['first_name', 'middle_names', 'last_name']:
            setattr(author, field, getattr(profile, field))
        author.save()


class Contributor(Member):
    """
    A resource contributor.

    Datacite definition:
        "The institution or person
        responsible for collecting,
        managing, distributing, or
        otherwise contributing to the
        development of the resource."

    """
    contributor_type_choices = (
        ('ContactPerson', 'Contact Person'),
        ('DataCollector', 'Data Collector'),
        ('DataCurator', 'Data Curator'),
        ('DataManager', 'Data Manager'),
        ('Distributor', 'Distributor'),
        ('Editor', 'Editor'),
        ('HostingInstitution', 'Hosting Institution'),
        ('Producer', 'Producer'),
        ('ProjectLeader', 'Project Leader'),
        ('ProjectManager', 'Project Manager'),
        ('ProjectMember', 'Project Member'),
        ('RegistrationAgency', 'Registration Agency'),
        ('RegistrationAuthority', 'Registration Authority'),
        ('RelatedPerson', 'Related Person'),
        ('Researcher', 'Researcher'),
        ('ResearchGroup', 'Research Group'),
        ('RightsHolder', 'Rights Holder'),
        ('Sponsor', 'Sponsor'),
        ('Supervisor', 'Supervisor'),
        ('WorkPackageLeader', 'Work Package Leader'),
        ('Other', 'Other'),
    )

    contributor_type = models.CharField(max_length=20,
        choices=contributor_type_choices)


class Metadata(models.Model):
    """
    Metadata for all projects.

    https://schema.datacite.org/
    https://schema.datacite.org/meta/kernel-4.0/doc/DataCite-MetadataKernel_v4.1.pdf
    https://www.nature.com/sdata/publish/for-authors#format

    """
    class Meta:
        abstract = True

    resource_types = (
        ('Database', 'Database'),
        ('Software', 'Software'),
        ('Tutorial', 'Tutorial'),
        ('Challenge', 'Challenge'),
    )

    title = models.CharField(max_length=200)
    # datacite: "A brief description of the resource and the context in
    # which the resource was created"
    abstract = RichTextField(max_length=10000, blank=True)
    background = RichTextField(blank=True)
    methods = RichTextField(blank=True)
    content_description = RichTextField(blank=True)
    technical_validation = RichTextField(blank=True)
    usage_notes = RichTextField(blank=True)

    acknowledgements = RichTextField(blank=True)
    paper_citations = models.ManyToManyField('project.Reference',
        related_name='%(class)s_citations', blank=True)
    references = models.ManyToManyField('project.Reference',
        related_name='%(class)s_references', blank=True)
    topics = models.ManyToManyField('project.Topic', related_name='%(class)s',
        blank=True)
    resource_type = models.CharField(max_length=10, choices=resource_types)
    # Access policy
    # Consideration: What happens when dua/training course objects change?
    dua = models.ForeignKey('project.DUA', null=True, blank=True,
        related_name='%(class)s')
    training_course = models.ForeignKey('project.TrainingCourse', null=True,
        blank=True, related_name='%(class)s')
    id_verification_required = models.BooleanField(default=False)

    # Version and changes (if any)
    version_number = models.CharField(max_length=15, default='', blank=True)
    changelog_summary = RichTextField(blank=True)
    # External home page
    project_home_page = models.URLField(default='', blank=True)


class Project(Metadata):
    """
    The model for user-owned projects.
    """
    creation_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)

    # Maximum allowed storage capacity in GB
    storage_allowance = models.SmallIntegerField(default=1)
    submitting_author = models.ForeignKey('user.User',
        related_name='submitting_projects')

    published = models.BooleanField(default=False)
    under_review = models.BooleanField(default=False)

    class Meta:
        unique_together = (('title', 'submitting_author'),)

    def __str__(self):
        return self.title

    def file_root(self):
        "Root directory containing the project's files"
        return os.path.join(MEDIA_ROOT, 'projects', str(self.id))

    def storage_used(self):
        "Total storage used in bytes"
        return get_tree_size(self.file_root())

@receiver(post_save, sender=Project)
@new_creation
def setup_project(sender, **kwargs):
    """
    When a Project is created:
    - create an Author object from the submitting_author field
    - create the project file directory
    """
    project = kwargs['instance']
    user = project.submitting_author
    Author.objects.create(project=project, user=user, display_order=1)
    # Create file directory
    os.mkdir(project.file_root())

class PublishedProject(Metadata):
    """
    A published project. Immutable snapshot.

    """
    slug = models.SlugField(max_length=30)
    # The Project this object was created from
    core_project = models.ForeignKey('project.Project',
        related_name='published_project', blank=True, null=True)
    # Total file storage size in bytes
    storage_size = models.IntegerField()
    publish_datetime = models.DateTimeField()
    is_newest_version = models.BooleanField(default=False)
    doi = models.CharField(max_length=50, default='', unique=True)

    class Meta:
        unique_together = (('title', 'version_number'),)


class Invitation(models.Model):
    """
    Invitation to join a project as an, author, or reviewer

    """
    project = models.ForeignKey('project.Project',
        related_name='invitations')
    # The target email
    email = models.EmailField(max_length=255)
    # User who made the invitation
    inviter = models.ForeignKey('user.User')
    # Either 'author', or 'reviewer'
    invitation_type = models.CharField(max_length=10)
    creation_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField()
    response = models.NullBooleanField(null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return ('Project: %s To: %s By: %s'
                % (self.project, self.email, self.inviter))

    def get_user_invitations(user, invitation_types='all'):
        "Get all active invitations to a user, possibly for a certain project"
        emails = [ae.email for ae in user.associated_emails.all()]
        invitations = Invitation.objects.filter(email__in=emails,
            is_active=True)
        if invitation_types != 'all':
            invitations = invitations.filter(
                invitation_type__in=invitation_types)

        return invitations

    def is_invited(user, project, invitation_types='all'):
        "Whether a user is invited to a project"
        user_invitations = get_user_invitations(user=user,
            invitation_types=invitation_types)

        return bool(project in [inv.project for inv in invitations])


class Topic(models.Model):
    """
    Topic information to tag projects
    """
    description = models.CharField(max_length=50)

    def __str__(self):
        return self.description


class Reference(models.Model):
    """
    General reference link and description
    """
    description = models.CharField(max_length=100)
    url = models.URLField()


class DUA(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=20, null=True)
    description = RichTextField()
    content = RichTextField()


class TrainingCourse(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=20, null=True)
    description = RichTextField()
    url = models.URLField()


class DUASignature(models.Model):
    user = models.ForeignKey('user.User', related_name='dua_signatures')
    date = models.DateField(auto_now_add=True)
    dua = models.ForeignKey('project.DUA', related_name='dua_signatures')


class TrainingCourseCompletion(models.Model):
    user = models.ForeignKey('user.User',
        related_name='training_course_completions')
    date = models.DateField(auto_now_add=True)
    training_course = models.ForeignKey('project.TrainingCourse',
        related_name='training_course_completions')


class StorageRequest(models.Model):
    """
    A request for storage capacity for a project
    """
    project = models.OneToOneField('project.Project')
    # Requested storage size in GB
    request_allowance = models.SmallIntegerField(
        validators=[MaxValueValidator(100), MinValueValidator(1)])
    request_datetime = models.DateTimeField(auto_now_add=True)
    response = models.NullBooleanField(null=True)
    is_active = models.BooleanField(default=True)
    # The authorizer
    responder = models.ForeignKey('user.User', null=True)


class Review(models.Model):
    """
    Project review
    """
    project = models.ForeignKey('project.Project', related_name='reviews')
    start_date = models.DateTimeField(auto_now_add=True)
    submission_date = models.DateTimeField(null=True)
    editor = models.ForeignKey('user.User', related_name='edits', null=True)
    reviewers = models.ManyToManyField('user.User', related_name='reviews')
