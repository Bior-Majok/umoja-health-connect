"""UI microcopy translations (NFR11 i18n framework).

English is authoritative. French and Swahili are direct translations of short UI
labels (not medical content, so no clinical vetting is required). Arabic includes
`dir: rtl` metadata consumed by the frontend to flip layout direction.

Health-education *content* (medical articles) is a separate concern — see
HealthEducationArticle.is_verified, which tracks whether a qualified reviewer has
signed off on the medical accuracy of translated content, per the SRS business rule.
"""

LANGUAGES = ['en', 'fr', 'sw', 'ar']
RTL_LANGUAGES = ['ar']

LABELS = {
    'login': {'en': 'Login', 'fr': 'Connexion', 'sw': 'Ingia', 'ar': 'تسجيل الدخول'},
    'register': {'en': 'Register', 'fr': "S'inscrire", 'sw': 'Jisajili', 'ar': 'تسجيل'},
    'logout': {'en': 'Log out', 'fr': 'Déconnexion', 'sw': 'Toka', 'ar': 'تسجيل الخروج'},
    'dashboard': {'en': 'Dashboard', 'fr': 'Tableau de bord', 'sw': 'Dashibodi', 'ar': 'لوحة التحكم'},
    'appointments': {'en': 'Appointments', 'fr': 'Rendez-vous', 'sw': 'Miadi', 'ar': 'المواعيد'},
    'medical_records': {'en': 'Medical Records', 'fr': 'Dossiers médicaux', 'sw': 'Rekodi za Afya', 'ar': 'السجلات الطبية'},
    'health_education': {'en': 'Health Education', 'fr': 'Éducation à la santé', 'sw': 'Elimu ya Afya', 'ar': 'التثقيف الصحي'},
    'emergency': {'en': 'Emergency', 'fr': 'Urgence', 'sw': 'Dharura', 'ar': 'طوارئ'},
    'book_appointment': {'en': 'Book Appointment', 'fr': 'Prendre un rendez-vous', 'sw': 'Weka Miadi', 'ar': 'حجز موعد'},
    'new_appointment': {'en': 'New appointment', 'fr': 'Nouveau rendez-vous', 'sw': 'Miadi mpya', 'ar': 'موعد جديد'},
    'add_record': {'en': 'Add record', 'fr': 'Ajouter un dossier', 'sw': 'Ongeza rekodi', 'ar': 'إضافة سجل'},
    'full_name': {'en': 'Full name', 'fr': 'Nom complet', 'sw': 'Jina kamili', 'ar': 'الاسم الكامل'},
    'phone_number': {'en': 'Phone number', 'fr': 'Numéro de téléphone', 'sw': 'Nambari ya simu', 'ar': 'رقم الهاتف'},
    'password': {'en': 'Password', 'fr': 'Mot de passe', 'sw': 'Nenosiri', 'ar': 'كلمة المرور'},
    'age': {'en': 'Age', 'fr': 'Âge', 'sw': 'Umri', 'ar': 'العمر'},
    'gender': {'en': 'Gender', 'fr': 'Genre', 'sw': 'Jinsia', 'ar': 'الجنس'},
    'country': {'en': 'Country', 'fr': 'Pays', 'sw': 'Nchi', 'ar': 'الدولة'},
    'region': {'en': 'Region', 'fr': 'Région', 'sw': 'Mkoa', 'ar': 'المنطقة'},
    'submit': {'en': 'Submit', 'fr': 'Soumettre', 'sw': 'Wasilisha', 'ar': 'إرسال'},
    'cancel': {'en': 'Cancel', 'fr': 'Annuler', 'sw': 'Ghairi', 'ar': 'إلغاء'},
    'save': {'en': 'Save', 'fr': 'Enregistrer', 'sw': 'Hifadhi', 'ar': 'حفظ'},
    'loading': {'en': 'Loading...', 'fr': 'Chargement...', 'sw': 'Inapakia...', 'ar': 'جارٍ التحميل...'},
    'welcome': {'en': 'Welcome', 'fr': 'Bienvenue', 'sw': 'Karibu', 'ar': 'مرحباً'},
    'profile': {'en': 'Profile', 'fr': 'Profil', 'sw': 'Wasifu', 'ar': 'الملف الشخصي'},
    'edit_profile': {'en': 'Edit profile', 'fr': 'Modifier le profil', 'sw': 'Hariri wasifu', 'ar': 'تعديل الملف الشخصي'},
    'symptoms': {'en': 'Symptoms', 'fr': 'Symptômes', 'sw': 'Dalili', 'ar': 'الأعراض'},
    'report_symptoms': {'en': 'Report symptoms', 'fr': 'Signaler des symptômes', 'sw': 'Ripoti dalili', 'ar': 'الإبلاغ عن الأعراض'},
    'consultation': {'en': 'Consultation', 'fr': 'Consultation', 'sw': 'Ushauri', 'ar': 'استشارة'},
    'date_time': {'en': 'Date & time', 'fr': 'Date et heure', 'sw': 'Tarehe na wakati', 'ar': 'التاريخ والوقت'},
    'notes': {'en': 'Notes', 'fr': 'Remarques', 'sw': 'Maelezo', 'ar': 'ملاحظات'},
    'doctor': {'en': 'Doctor', 'fr': 'Médecin', 'sw': 'Daktari', 'ar': 'طبيب'},
    'clinic': {'en': 'Clinic', 'fr': 'Clinique', 'sw': 'Kliniki', 'ar': 'عيادة'},
    'status': {'en': 'Status', 'fr': 'Statut', 'sw': 'Hali', 'ar': 'الحالة'},
    'upcoming': {'en': 'Upcoming', 'fr': 'À venir', 'sw': 'Ijayo', 'ar': 'قادم'},
    'completed': {'en': 'Completed', 'fr': 'Terminé', 'sw': 'Imekamilika', 'ar': 'مكتمل'},
    'cancelled': {'en': 'Cancelled', 'fr': 'Annulé', 'sw': 'Imeghairiwa', 'ar': 'ملغى'},
    'normal': {'en': 'Normal', 'fr': 'Normal', 'sw': 'Kawaida', 'ar': 'طبيعي'},
    'flagged': {'en': 'Flagged', 'fr': 'Signalé', 'sw': 'Imebainishwa', 'ar': 'محدد'},
    'home': {'en': 'Home', 'fr': 'Accueil', 'sw': 'Nyumbani', 'ar': 'الرئيسية'},
    'get_started': {'en': 'Get Started', 'fr': 'Commencer', 'sw': 'Anza', 'ar': 'ابدأ'},
    'language': {'en': 'Language', 'fr': 'Langue', 'sw': 'Lugha', 'ar': 'اللغة'},
    'family_contact': {'en': 'Family contact', 'fr': 'Contact familial', 'sw': 'Mawasiliano ya familia', 'ar': 'جهة اتصال العائلة'},
}


def labels_for(lang):
    lang = lang if lang in LANGUAGES else 'en'
    return {
        'language': lang,
        'dir': 'rtl' if lang in RTL_LANGUAGES else 'ltr',
        'labels': {key: values.get(lang, values['en']) for key, values in LABELS.items()},
    }
