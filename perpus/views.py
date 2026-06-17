from django.shortcuts import render ,redirect
from django.db import connection
from django.utils.html import escape
from django.http import HttpResponse

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """Mengubah satu hasil query menjadi dictionary."""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()

    if row is None:
        return None

    return dict(zip(columns, row))

def perpus_list(request):
    return render(request, 'home.html')

def daftar_buku(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok " \
        "FROM buku " \
        "ORDER BY id DESC")
        buku_list = dictfetchall(cursor)

    return render(request, 'daftar_buku.html', {
        'perpus_list': buku_list})

def buku_create(request):
    with connection.cursor() as cursor:
        if request.method == 'POST':
            judul = escape(request.POST.get('judul'))
            pengarang = escape(request.POST.get('pengarang'))
            kategori = escape(request.POST.get('kategori'))
            penerbit = escape(request.POST.get('penerbit'))
            tahun_terbit = escape(request.POST.get('tahun_terbit'))
            rak = escape(request.POST.get('rak'))
            stok = escape(request.POST.get('stok'))

            cursor.execute("INSERT INTO buku (judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok])

            return redirect('daftar_buku')
        
    return render(request, 'tambah_buku.html')
 
def buku_detail(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok "\
        "FROM buku WHERE id = %s", [id])
        buku = dictfetchone(cursor)


    return render(request, 'detail_buku.html', {'buku': buku})

def buku_update(request, id):
    with connection.cursor() as cursor:
        if request.method == 'POST':
            judul = escape(request.POST.get('judul'))
            pengarang = escape(request.POST.get('pengarang'))
            kategori = escape(request.POST.get('kategori'))
            penerbit = escape(request.POST.get('penerbit'))
            tahun_terbit = escape(request.POST.get('tahun_terbit'))
            rak = escape(request.POST.get('rak'))
            stok = escape(request.POST.get('stok'))

            cursor.execute("UPDATE buku SET judul = %s, pengarang = %s, kategori = %s, penerbit = %s, tahun_terbit = %s, rak = %s, stok = %s WHERE id = %s",
            [judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, id])

            return redirect('daftar_buku')
        
        cursor.execute("SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok "\
        "FROM buku WHERE id = %s", [id])
        buku = dictfetchone(cursor)

    return render(request, 'edit_buku.html', {'buku': buku})
    

def buku_delete(request, id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM buku WHERE id = %s", [id])
    return redirect('daftar_buku')

# PEMINJAMAN

def daftar_peminjaman(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.id,
                s.nama AS nama_siswa,
                b.judul AS judul_buku,
                p.tanggal_pinjam,
                p.jatuh_tempo,
                p.keperluan,
                p.status,
                p.petugas
            FROM peminjaman p
            JOIN siswa s ON p.siswa_id = s.id
            JOIN buku b ON p.buku_id = b.id
            ORDER BY p.id DESC
        """)
        peminjaman_list = dictfetchall(cursor)

    return render(request, 'daftar_peminjam.html', {
        'peminjaman_list': peminjaman_list
    })

def peminjaman_create(request):
    with connection.cursor() as cursor:

        if request.method == 'POST':
            siswa_id = request.POST.get('siswa_id')
            buku_id = request.POST.get('buku_id')
            tanggal_pinjam = request.POST.get('tanggal_pinjam')
            jatuh_tempo = request.POST.get('jatuh_tempo')
            keperluan = request.POST.get('keperluan')
            petugas = request.POST.get('petugas')
            status = 'Dipinjam'

            cursor.execute(
                "SELECT stok FROM buku WHERE id = %s",
                [buku_id]
            )

            stok = cursor.fetchone()[0]

            if stok <= 0:
                return HttpResponse("Stok buku habis")

            cursor.execute("""
                INSERT INTO peminjaman
                (siswa_id, buku_id, tanggal_pinjam, jatuh_tempo, keperluan, petugas, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                siswa_id,
                buku_id,
                tanggal_pinjam,
                jatuh_tempo,
                keperluan,
                petugas,
                status
            ])

            cursor.execute("""
                UPDATE buku
                SET stok = stok - 1
                WHERE id = %s
            """, [buku_id])

            return redirect('daftar_peminjaman')

        # ambil data siswa
        cursor.execute("""
            SELECT id, nama, kelas, nis
            FROM siswa
            ORDER BY nama
        """)
        siswa_list = dictfetchall(cursor)

        # ambil data buku
        cursor.execute("""
            SELECT id, judul, stok
            FROM buku
            ORDER BY judul
        """)
        buku_list = dictfetchall(cursor)

    return render(request, 'tambah_peminjaman.html', {
        'siswa_list': siswa_list,
        'buku_list': buku_list,
    })

def peminjaman_kembali(request, id):
    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT buku_id, status
            FROM peminjaman
            WHERE id = %s
        """, [id])

        hasil = cursor.fetchone()

        if hasil is None:
            return redirect('daftar_peminjaman')

        buku_id = hasil[0]
        status = hasil[1]

        # Jika sudah dikembalikan, jangan tambah stok lagi
        if status == 'Dikembalikan':
            return redirect('daftar_peminjaman')

        cursor.execute("""
            UPDATE peminjaman
            SET status = 'Dikembalikan'
            WHERE id = %s
        """, [id])

        cursor.execute("""
            UPDATE buku
            SET stok = stok + 1
            WHERE id = %s
        """, [buku_id])

    return redirect('daftar_peminjaman')

def peminjaman_delete(request, id):
    with connection.cursor() as cursor:

        # Ambil buku yang dipinjam
        cursor.execute("""
            DELETE FROM peminjaman
            WHERE id = %s
        """, [id])

    return redirect('daftar_peminjaman')

def daftar_siswa(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id,
                nama,
                kelas,
                nis,
                is_active
            FROM siswa
            ORDER BY id DESC
        """)
        siswa_list = dictfetchall(cursor)

    return render(request, 'daftar_siswa.html', {
        'siswa_list': siswa_list
    })

def siswa_detail(request, id):
    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                s.id,
                s.nama,
                s.kelas,
                s.nis,
                s.is_active,

                COUNT(p.id) AS total_peminjaman,

                COUNT(
                    CASE
                        WHEN p.status = 'Dipinjam'
                        THEN 1
                    END
                ) AS peminjaman_aktif

            FROM siswa s
            LEFT JOIN peminjaman p
                ON s.id = p.siswa_id

            WHERE s.id = %s

            GROUP BY
                s.id,
                s.nama,
                s.kelas,
                s.nis,
                s.is_active
        """, [id])

        siswa = dictfetchone(cursor)

    return render(request, 'detail_siswa.html', {
        'siswa': siswa
    })








def siswa_create(request):
    with connection.cursor() as cursor:

        if request.method == 'POST':
            nama = request.POST.get('nama')
            kelas = request.POST.get('kelas')
            nis = request.POST.get('nis')
            status = request.POST.get('status') == 'true'

            cursor.execute(
                "INSERT INTO siswa (nama, kelas, nis, is_active) VALUES (%s, %s, %s, %s)",
                [nama, kelas, nis, status]
            )

            return redirect('daftar_siswa')

        cursor.execute("""
            SELECT DISTINCT kelas
            FROM siswa
            ORDER BY kelas
        """)
        kelas_list = dictfetchall(cursor)

    return render(request, 'tambah_siswa.html', {
        'kelas_list': kelas_list
    })





def siswa_update(request, id):
    with connection.cursor() as cursor:

        if request.method == 'POST':
            nama = escape(request.POST.get('nama'))
            kelas = escape(request.POST.get('kelas'))
            nis = escape(request.POST.get('nis'))
            is_active = request.POST.get('is_active') == 'true'

            cursor.execute("""
                UPDATE siswa
                SET nama = %s, kelas = %s, nis = %s, is_active = %s
                WHERE id = %s
            """, [nama, kelas, nis, is_active, id])

            return redirect('daftar_siswa')

        cursor.execute("""
            SELECT id, nama, kelas, nis, is_active
            FROM siswa
            WHERE id = %s
        """, [id])
        siswa = dictfetchone(cursor)

        cursor.execute("""
            SELECT DISTINCT kelas
            FROM siswa
            ORDER BY kelas
        """)
        kelas_list = dictfetchall(cursor)

    return render(request, 'edit_siswa.html', {
        'siswa': siswa,
        'kelas_list': kelas_list
    })
    







def siswa_delete(request, id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM siswa WHERE id = %s", [id])
    return redirect('daftar_siswa')


def dashboard(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM siswa")
        total_siswa = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM buku")
        total_buku = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE status = 'Dipinjam'")
        total_peminjaman_aktif = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE status = 'Dikembalikan'")
        total_peminjaman_selesai = cursor.fetchone()[0]
           



    return render(request, 'home.html', {
        'total_siswa': total_siswa,
        'total_buku': total_buku,
        'total_peminjaman_aktif': total_peminjaman_aktif,
        'total_peminjaman_selesai': total_peminjaman_selesai
    })


    





