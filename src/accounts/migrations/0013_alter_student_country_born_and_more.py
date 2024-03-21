# Generated by Django 5.0.2 on 2024-03-20 03:20

import accounts.models
import django.core.validators
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_student_certificate_photo_student_country_born_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='country_born',
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name='student',
            name='country_of_residence',
            field=models.CharField(choices=[('AF', 'أفغانستان'), ('AL', 'ألبانيا'), ('DZ', 'الجزائر'), ('AD', 'أندورا'), ('AO', 'أنجولا'), ('AI', 'أنجويلا'), ('AR', 'الأرجنتين'), ('AM', 'أرمينيا'), ('AW', 'آروبا'), ('AU', 'أستراليا'), ('AT', 'النمسا'), ('AZ', 'أذربيجان'), ('BS', 'الباهاما'), ('BH', 'البحرين'), ('BD', 'بنجلاديش'), ('BB', 'بربادوس'), ('BE', 'بلجيكا'), ('BZ', 'بليز'), ('BJ', 'بنين'), ('BM', 'برمودا'), ('BT', 'بوتان'), ('BO', 'بوليفيا'), ('BW', 'بتسوانا'), ('BR', 'البرازيل'), ('BN', 'بروناي'), ('BG', 'بلغاريا'), ('BI', 'بوروندي'), ('KH', 'كمبوديا'), ('CM', 'الكاميرون'), ('CA', 'كندا'), ('TD', 'تشاد'), ('CL', 'شيلي'), ('CN', 'الصين'), ('CO', 'كولومبيا'), ('CG', 'الكونغو'), ('CR', 'كوستاريكا'), ('HR', 'كرواتيا'), ('CU', 'كوبا'), ('CW', 'كوراساو'), ('CY', 'قبرص'), ('CZ', 'تشيكيا'), ('DK', 'الدنمارك'), ('DJ', 'جيبوتي'), ('DM', 'دومينيكا'), ('EC', 'الاكوادور'), ('EG', 'مصر'), ('SV', 'السلفادور'), ('ER', 'إريتريا'), ('EE', 'استونيا'), ('SZ', 'إيسواتيني'), ('ET', 'اثيوبيا'), ('FJ', 'فيجي'), ('FI', 'فنلندا'), ('FR', 'فرنسا'), ('GF', 'غويانا'), ('GA', 'الجابون'), ('GM', 'غامبيا'), ('GE', 'جورجيا'), ('DE', 'ألمانيا'), ('GH', 'غانا'), ('GR', 'اليونان'), ('GL', 'جرينلاند'), ('GD', 'جرينادا'), ('GP', 'جوادلوب'), ('GU', 'جوام'), ('GT', 'جواتيمالا'), ('GG', 'جيرنزي'), ('GN', 'غينيا'), ('GY', 'غيانا'), ('HT', 'هايتي'), ('HN', 'هندوراس'), ('HU', 'المجر'), ('IS', 'أيسلندا'), ('IN', 'الهند'), ('ID', 'اندونيسيا'), ('IR', 'إيران'), ('IQ', 'العراق'), ('IE', 'أيرلندا'), ('IL', 'إسرائيل'), ('IT', 'إيطاليا'), ('JM', 'جامايكا'), ('JP', 'اليابان'), ('JE', 'جيرسي'), ('JO', 'الأردن'), ('KZ', 'كازاخستان'), ('KE', 'كينيا'), ('KI', 'كيريباتي'), ('KW', 'الكويت'), ('KG', 'قرغيزستان'), ('LA', 'لاوس'), ('LV', 'لاتفيا'), ('LB', 'لبنان'), ('LS', 'ليسوتو'), ('LR', 'ليبيريا'), ('LY', 'ليبيا'), ('LI', 'ليختنشتاين'), ('LT', 'ليتوانيا'), ('LU', 'لوكسمبورج'), ('MO', 'ماكاو'), ('MG', 'مدغشقر'), ('MW', 'ملاوي'), ('MY', 'ماليزيا'), ('ML', 'مالي'), ('MT', 'مالطا'), ('MQ', 'مارتينيك'), ('MR', 'موريتانيا'), ('MU', 'موريشيوس'), ('YT', 'مايوت'), ('MX', 'المكسيك'), ('MD', 'مولدافيا'), ('MC', 'موناكو'), ('MN', 'منغوليا'), ('MS', 'مونتسرات'), ('MA', 'المغرب'), ('MZ', 'موزمبيق'), ('MM', 'ميانمار'), ('NA', 'ناميبيا'), ('NR', 'نورو'), ('NP', 'نيبال'), ('NL', 'هولندا'), ('NZ', 'نيوزيلاندا'), ('NI', 'نيكاراجوا'), ('NE', 'النيجر'), ('NG', 'نيجيريا'), ('NU', 'نيوي'), ('NO', 'النرويج'), ('OM', 'عُمان'), ('PK', 'باكستان'), ('PW', 'بالاو'), ('PS', 'فلسطين'), ('PA', 'بنما'), ('PY', 'باراجواي'), ('PE', 'بيرو'), ('PH', 'الفيلبين'), ('PN', 'بتكايرن'), ('PL', 'بولندا'), ('PT', 'البرتغال'), ('PR', 'بورتوريكو'), ('QA', 'قطر'), ('RE', 'روينيون'), ('RO', 'رومانيا'), ('RU', 'روسيا'), ('RW', 'رواندا'), ('WS', 'ساموا'), ('SN', 'السنغال'), ('RS', 'صربيا'), ('SC', 'سيشل'), ('SL', 'سيراليون'), ('SG', 'سنغافورة'), ('SK', 'سلوفاكيا'), ('SI', 'سلوفينيا'), ('SO', 'الصومال'), ('ES', 'أسبانيا'), ('LK', 'سريلانكا'), ('SD', 'السودان'), ('SR', 'سورينام'), ('SE', 'السويد'), ('CH', 'سويسرا'), ('SY', 'سوريا'), ('TW', 'تايوان'), ('TJ', 'طاجكستان'), ('TZ', 'تانزانيا'), ('TH', 'تايلند'), ('TG', 'توجو'), ('TK', 'توكيلو'), ('TO', 'تونجا'), ('TN', 'تونس'), ('TR', 'تركيا'), ('TM', 'تركمانستان'), ('TV', 'توفالو'), ('UG', 'أوغندا'), ('UA', 'أوكرانيا'), ('UY', 'أورجواي'), ('UZ', 'أوزبكستان'), ('VU', 'فانواتو'), ('VE', 'فنزويلا'), ('VN', 'فيتنام'), ('YE', 'اليمن'), ('ZM', 'زامبيا'), ('ZW', 'زيمبابوي'), ('AX', 'جزر آلاند'), ('AS', 'ساموا الأمريكية'), ('AQ', 'القطب الجنوبي'), ('AG', 'أنتيجوا وبربودا'), ('BY', 'روسيا البيضاء'), ('BA', 'البوسنة والهرسك'), ('BV', 'جزيرة بوفيه'), ('BF', 'بوركينا فاسو'), ('CV', 'كابو فيردي'), ('KY', 'جزر الكايمن'), ('CX', 'جزيرة الكريسماس'), ('CC', 'جزر كوكس'), ('KM', 'جزر القمر'), ('CK', 'جزر كوك'), ('CI', 'ساحل العاج'), ('DO', 'جمهورية الدومينيك'), ('GQ', 'غينيا الاستوائية'), ('FO', 'جزر فارو'), ('PF', 'بولينيزيا الفرنسية'), ('GI', 'جبل طارق'), ('GW', 'غينيا بيساو'), ('VA', 'الكرسي الرسولي'), ('IM', 'جزيرة مان'), ('KP', 'كوريا الشمالية'), ('KR', 'كوريا الجنوبية'), ('MV', 'جزر الملديف'), ('MH', 'جزر المارشال'), ('ME', 'الجبل الأسود'), ('NC', 'كاليدونيا الجديدة'), ('NF', 'جزيرة نورفوك'), ('MK', 'مقدونيا الشمالية'), ('BL', 'سانت بارتيليمي'), ('SH', 'سانت هيلنا'), ('LC', 'سانت لوسيا'), ('SM', 'سان مارينو'), ('SB', 'جزر سليمان'), ('SS', 'جنوب السودان'), ('TL', 'تيمور الشرقية'), ('TT', 'ترينيداد وتوباغو'), ('GB', 'المملكة المتحدة'), ('EH', 'الصحراء الغربية'), ('BQ', 'الجزر الكاريبية الهولندية'), ('IO', 'المحيط الهندي البريطاني'), ('CF', 'جمهورية افريقيا الوسطى'), ('CD', 'جمهورية الكونغو الديمقراطية'), ('TF', 'المقاطعات الجنوبية الفرنسية'), ('HM', 'جزيرة هيرد وماكدونالد'), ('HK', 'هونج كونج الصينية'), ('MP', 'جزر ماريانا الشمالية'), ('PG', 'بابوا غينيا الجديدة'), ('KN', 'سانت كيتس ونيفيس'), ('PM', 'سانت بيير وميكولون'), ('VC', 'سانت فنسنت وغرنادين'), ('ST', 'ساو تومي وبرينسيبي'), ('SJ', 'سفالبارد وجان مايان'), ('TC', 'جزر الترك وجايكوس'), ('AE', 'الإمارات العربية المتحدة'), ('US', 'الولايات المتحدة الأمريكية'), ('WF', 'جزر والس وفوتونا'), ('GS', 'جورجيا الجنوبية وجزر ساندويتش الجنوبية'), ('UM', 'جزر الولايات المتحدة البعيدة الصغيرة'), ('MF', 'سانت مارتن (الجزء الفرنسي)'), ('SX', 'سانت مارتن (الجزء الهولندي)'), ('VI', 'جزر العذراء (الولايات المتحدة)'), ('FK', 'جزر فوكلاند (مالفيناس)'), ('ZA', 'جنوب افريقيا (الجمهورية)'), ('VG', 'جزر العذراء (البريطانية)'), ('FM', 'ميكرونيسيا (الولايات المتحدة)'), ('SA', 'السعودية (المملكة العربية)'), ('', 'Select Country')], max_length=200, null=True, verbose_name='بلد الإقامة'),
        ),
        migrations.AlterField(
            model_name='student',
            name='id_photo',
            field=models.ImageField(upload_to=accounts.models.student_id_photo_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], verbose_name='صورة إثبات الشخصية (جواز السفر أو بطاقة الهوية أو قيد مدني)'),
        ),
    ]
