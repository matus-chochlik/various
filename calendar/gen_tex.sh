#!/bin/bash
# Copyright (c) 2015-2017 Matus Chochlik

temp_dir="$(mktemp -d)"

function cal_cleanup()
{
	rm -rf ${temp_dir}
}

trap cal_cleanup EXIT

imgdir=${1}

if [[ "${imgdir}" == "" ]]
then echo "No image directory specified" && exit 1
fi
if [[ ! -d "${imgdir}" ]]
then echo "'${imgdir}' is not a directory" && exit 1
fi

year=${2:-$(date +%Y -d '+1 year')}

extradays=$(($(date +%u -d "${year}-01-01 -1 day") % 7))
yearweeks=$(($(date +%W -d "${year}-12-31")+1))

language=${3:-sk}
country=${4:-SK}
input_dir=${5:-$(dirname ${0})}

function cal_translate()
{
	grep -e "^${1}|" < ${input_dir}/dict/${language}.txt |
	cut -d'|' -f2 
}

function babel_lang_name()
{
	case ${language}_${country} in
	sk_SK) echo "slovak";;
	en_UK) echo "british";;
	*) echo "english";;
	esac
}

function cal_begin_document()
{
echo "\\documentclass{article}"
echo "\\usepackage[utf8]{inputenc}"
echo "\\usepackage[$(babel_lang_name)]{babel}"
echo "\\usepackage{nopageno}"
echo "\\usepackage{geometry}"
echo "\\geometry{"
echo "	paperwidth=29.7cm,"
echo "	paperheight=21.0cm,"
echo "	layoutwidth=28.9cm,"
echo "	layoutheight=17.5cm,"
echo "	layoutvoffset={1.75cm},"
echo "	layouthoffset={0.40cm},"
echo "	margin={0cm},"
echo "	showcrop"
echo "}"
echo "\\usepackage{graphicx}"
echo "\\DeclareGraphicsExtensions{.png}"
echo "\\usepackage[dvipsnames]{xcolor}"
echo "\\definecolor{Workday0Color}{gray}{0.92}"
echo "\\definecolor{Workday1Color}{gray}{0.98}"
echo "\\definecolor{Holiday0Color}{rgb}{0.8,0.9,0.7}"
echo "\\definecolor{Holiday1Color}{rgb}{0.7,0.8,0.6}"
echo "\\usepackage{shadowtext}"
echo "\\usepackage{transparent}"
echo "\\usepackage{tikz}"
echo "\\usetikzlibrary{calendar}"


if [[ -f ${imgdir}/background.pdf ]]
then
	echo "\\usepackage[pages=all]{background}"
	echo "\\backgroundsetup{"
	echo "scale=1.0,"
	echo "color=white,"
	echo "opacity=1,"
	echo "angle=0,"
	echo "contents={"
	echo "  \\includegraphics[width=\\textwidth,height=\\textheight]{${imgdir}/background.pdf}"
	echo "  }"
	echo "}"
fi

echo
echo "\\begin{document}"
echo
}

function cal_end_document()
{
echo
echo "\\end{document}"
}

function cal_year_image()
{
	echo "\\mbox{"
	echo "\\begin{minipage}[c]{0.55\\linewidth}"
	echo "  \\mbox{"
	echo "  \\begin{minipage}[c]{\\linewidth}"
	echo "    \\includegraphics[width=16.0cm]{${imgdir}/00.png}"
	echo "  \\end{minipage}"
	echo "  }"
	echo "\\end{minipage}"
	echo "}"
}

function cal_page_image()
{
	week=${1}
	extradays=${2}
	week_id=$(printf "%02d" ${week})
	week_no=$(date +%W --date "${year}-01-01 +$((week)) weeks -${extradays} days")
	week_str="${week_no}. $(cal_translate week)"
	month_name1=$(cal_translate month$(date +%m --date "${year}-01-01 +$((week-1)) weeks -${extradays} days"))
	month_name2=$(cal_translate month$(date +%m --date "${year}-01-01 +$((week-1)) weeks +6 days -${extradays} days"))

	if [[ "${month_name1}" == "${month_name2}" ]]
	then month_name="${month_name1^}"
	else month_name="${month_name1^}/${month_name2^}"
	fi

	echo "\\mbox{"
	echo "\\begin{minipage}[c]{0.58\\linewidth}"
	echo "  \\mbox{"
	echo "  \\begin{minipage}[c]{\\linewidth}"
	echo "    \\centering"
	echo "    \\hspace{2cm}"
	echo "    \\shadowtext{\\fontsize{16}{18}\\selectfont\\usefont{T1}{qag}{m}{n}{${week_str}}}"
	echo "    \\hfill"
	echo "    \\shadowtext{\\fontsize{24}{27}\\selectfont\\usefont{T1}{qag}{b}{sc}${month_name^}~}"
	echo "    \\hfill"
	echo "  \\end{minipage}"
	echo "  }"
	echo "  \\mbox{"
	echo "  \\begin{minipage}[c]{\\linewidth}"
	echo "    \\includegraphics[width=16.6cm]{${imgdir}/${week_id}.png}"
	echo "  \\end{minipage}"
	echo "  }"
	echo "  \\mbox{"
	echo "  \\begin{minipage}[c]{\\linewidth}"
	echo "  \\vspace{6mm}"
	echo "	\\normalsize{\\selectfont\\usefont{T1}{qag}{m}{sc}"
	cat "${imgdir}/${week_id}.txt"
	echo "  }"
	echo "  \\end{minipage}"
	echo "  }"
	echo "\\end{minipage}"
	echo "}"
}

function cal_year_table()
{
	echo "\\mbox{"
	echo "\\begin{minipage}[c]{0.45\\linewidth}"
	echo "\\begin{tikzpicture}[every calendar/.style={"
	echo "  font=\\footnotesize,"
	echo "  month label above centered"
	echo "}]"
	echo "  \\matrix[column sep=1.0em, row sep=1.0em] {"

	for row in 0 1 2 3
	do
		m1=$((row*3+1))
		m2=$((row*3+2))
		m3=$((row*3+3))
		mts="\\normalsize{\\textbf{\\textit{"
		mn1=$(cal_translate month$(printf "%02d" ${m1}))
		mn2=$(cal_translate month$(printf "%02d" ${m2}))
		mn3=$(cal_translate month$(printf "%02d" ${m3}))
		mte="}}}"
		echo -n "    \\calendar[month text=${mts}${mn1^}${mte}, "
		echo -n "dates=${year}-${m1}-01 to ${year}-${m1}-last,week list];"
		echo -n "\\pgfmatrixnextcell"
		echo -n "\\calendar[month text=${mts}${mn2^}${mte}, "
		echo -n "dates=${year}-${m2}-01 to ${year}-${m2}-last,week list];"
		echo -n "\\pgfmatrixnextcell"
		echo "\\calendar[month text=${mts}${mn3^}${mte}, "
		echo "dates=${year}-${m3}-01 to ${year}-${m3}-last,week list]; \\\\"
	done

	echo "  };"
	echo "\\end{tikzpicture}"
	echo "\\end{minipage}"
	echo "}"
}

function cal_page_table()
{
	week=${1}
	extradays=${2}

	echo "\\mbox{"
	echo "\\begin{minipage}[c]{0.35\\linewidth}"

	for weekday in {1..7}
	do
		d=$((weekday-1-extradays))
		dspec="${year}-01-01 +$((week-1)) weeks + ${d} days"
		day_no=$(date +%d --date "${dspec}")
		month_no=$(date +%m --date "${dspec}")
		monthday=$(date +%e --date "${dspec}")
		dayname=$(cal_translate weekday${weekday})

		holidays=0
		weekend=0
		items=0

		stable_holiday_file="${input_dir}/holidays/${country}/stable/${month_no}.txt"
		movable_holiday_file="${input_dir}/holidays/${country}/movable/${year}/${month_no}.txt"
		holiday_file="${temp_dir}/holidays${year}${month_no}.txt"

		items_file="${input_dir}/items/${country}/${month_no}.txt"

		rm -f ${holiday_file}

		if [[ ${weekday} -gt 5 ]]
		then let weekend=1
		fi

		if [[ -f ${stable_holiday_file} ]]
		then
			if [[ $(grep -c -e "^${day_no}|." < ${stable_holiday_file}) -ne 0 ]]
			then
				let holidays=1
				cat ${stable_holiday_file} >> ${holiday_file}
			fi
		fi
		if [[ -f ${movable_holiday_file} ]]
		then
			if [[ $(grep -c -e "^${day_no}|." < ${movable_holiday_file}) -ne 0 ]]
			then
				let holidays=1
				cat ${movable_holiday_file} >> ${holiday_file}
			fi
		fi
		if [[ -f ${items_file} ]]
		then
			if [[ $(grep -c -e "^${day_no}|." < ${items_file}) -ne 0 ]]
			then let items=1
			fi
		fi


		if let holidays+weekend
		then echo "  \\colorbox{Holiday$((weekday%2))Color}{"
		else echo "  \\colorbox{Workday$((weekday%2))Color}{"
		fi
		echo "  \\begin{minipage}[c]{0.957\\linewidth}"
		echo "    \\mbox{"
		echo "    \\begin{minipage}[c]{1.4cm}"
		echo "      \\centering"
		echo -n "      \\shadowtext{\\fontsize{30}{34}"
		echo -n        "\\selectfont\\usefont{T1}{qag}{b}{sc}"
		echo           "${monthday}}"
		echo "    \\end{minipage}"
		echo "    }"
		echo "    \\mbox{"
		echo "    \\begin{minipage}[c]{6cm}"
		echo "      \\vspace{1mm}"
		echo -n "      \\shadowtext{\\fontsize{13}{15}"
		echo -n        "\\selectfont\\usefont{T1}{qag}{b}{n}"
		echo           "${dayname^}}\\\\"
		echo "      \\vfill"
		echo -n "      {\\fontsize{10}{10}"
		echo -n        "\\selectfont\\usefont{T1}{qag}{n}{n}"

		# holidays
		if let holidays
		then 
			grep -e "^${day_no}|" < ${holiday_file} |
			head -1 |
			cut -d'|' -f2 |
			while read line
			do echo -n "      {\\color{BrickRed} ${line}"
			done

			grep -e "^${day_no}|" < ${holiday_file} |
			tail -n +2 |
			cut -d'|' -f2 |
			while read line
			do echo -n "\\\\${line}"
			done
			echo -n "}"

			if let items
			then echo -n "\\\\"
			fi
		fi

		# items (names, ...)
		if let items
		then
			grep -e "^${day_no}|" < ${items_file} |
			head -1 |
			cut -d'|' -f2 |
			while read line
			do echo -n "      ${line}"
			done

			grep -e "^${day_no}|" < ${items_file} |
			tail -n +2 |
			cut -d'|' -f2 |
			while read line
			do echo -n "\\\\${line}"
			done
		fi

		echo "}"

		echo "      \\vspace{1mm}"
		echo "    \\end{minipage}"
		echo "    }"
		echo "    \\begin{minipage}[c]{1cm}"
		echo "      \\vspace{1.75cm}"
		echo "    \\end{minipage}"
		echo "  \\end{minipage}"
		echo "  }"
		echo "  \\hrule"
	done

	echo "  \\vspace{0.5cm}"
	if [[ -f ${imgdir}/side_decor_h.pdf ]]
	then echo "  \\includegraphics[height=0.8cm]{${imgdir}/side_decor_h.pdf}"
	fi
	echo "\\end{minipage}"
	echo "}"
}

function cal_page_decor()
{
	echo "\\mbox{"
	echo "\\begin{minipage}[c]{1.0cm}"
	if [[ -f ${imgdir}/side_decor_v.pdf ]]
	then echo "  \\includegraphics[width=0.8cm]{${imgdir}/side_decor_v.pdf}"
	fi
	echo "\\end{minipage}"
	echo "}"
}

function cal_cover_page()
{
	echo "\\noindent"
	echo "\\includegraphics[width=\\textwidth,height=\\textheight]{${imgdir}/CC.png}"

	echo "\\newpage"
	echo "\\clearpage"
}

function cal_year_page()
{
	echo "\\noindent"
	echo "\\mbox{"
	echo "\\begin{minipage}[t]{\\linewidth}"
	echo "      \\vspace{1.20cm}"
	echo "\\end{minipage}"
	echo "}"
	echo "\\hrule"
	echo "\\noindent"
	echo "\\mbox{"
	echo "\\begin{minipage}[b]{\\linewidth}"
	cal_year_image "${imgdir}" ${year}
	echo "\\hfill"
	cal_year_table "${imgdir}" ${year}
	echo "\\end{minipage}"
	echo "}"
	echo "\\hrule"
	echo "\\newpage"
	echo "\\clearpage"
}

function cal_single_page()
{
	week=${1}
	extradays=${2}
	echo "\\noindent"
	echo "\\mbox{"
	echo "\\begin{minipage}[t]{\\linewidth}"
	echo "      \\vspace{1.20cm}"
	echo "\\end{minipage}"
	echo "}"
	echo "\\hrule"
	echo "\\noindent"
	echo "\\mbox{"
	echo "\\begin{minipage}[b]{\\linewidth}"
	cal_page_image ${week} ${extradays}
	echo "\\hfill"
	cal_page_table ${week} ${extradays}
	echo "\\hfill"
	cal_page_decor ${week} ${extradays}
	echo "\\end{minipage}"
	echo "}"
	echo "\\newpage"
	echo "\\clearpage"
}

(
cal_begin_document
cal_cover_page
cal_year_page
for week in $(seq 1 $((yearweeks)))
do cal_single_page ${week} ${extradays}
done
cal_end_document
)
