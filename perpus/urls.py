from django.urls import path
from . import views

urlpatterns = [
    path('', views.perpus_list, name='perpus_list'),

    # PEMINJAMAN
    path('peminjaman/', views.daftar_peminjaman, name='daftar_peminjaman'),
    path('peminjaman/tambah/', views.peminjaman_create, name='peminjaman_create'),
    path('peminjaman/<int:id>/kembali/', views.peminjaman_kembali, name='peminjaman_kembali'),
    path('peminjaman/<int:id>/hapus/', views.peminjaman_delete, name='peminjaman_delete'),
    # SISWA
    path('siswa/', views.daftar_siswa, name='daftar_siswa'),
    path('siswa/tambah/', views.siswa_create, name='siswa_create'),
    path('siswa/<int:id>/', views.siswa_detail, name='siswa_detail'),
    path('siswa/<int:id>/edit/', views.siswa_update, name='siswa_update'),
    path('siswa/<int:id>/hapus/', views.siswa_delete, name='siswa_delete'),

    # BUKU
    path('daftar-buku/', views.daftar_buku, name='daftar_buku'),
    path('tambah/', views.buku_create, name='buku_create'),
    path('<int:id>/', views.buku_detail, name='buku_detail'),
    path('<int:id>/edit/', views.buku_update, name='buku_update'),
    path('<int:id>/hapus/', views.buku_delete, name='buku_delete'),
    
    #dashbord
    path('dashboard/', views.dashboard, name='dashboard')
]