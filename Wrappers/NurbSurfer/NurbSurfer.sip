//SIP wrapper to the NurbSurfer library.

%Module NurbSurfer

%Import QtCore/QtCoremod.sip

struct Vertex {

%TypeHeaderCode
#include <vertex.h>
%End
		Vertex();
		Vertex(double x, double y, double z);
    double x;
    double y;
	  double z;
	  QList<double> get_xyz();
	  QString to_string();
};


class Nurbs {

%TypeHeaderCode
#include <nurbs.h>
%End

public:
    Nurbs();
    void set_controls(QList<Vertex> controls);
    Vertex C(double u);
    QList<Vertex> range(int divisions);
    QList<double> get_knots();
    void set_knots(QList<double> newKnots);
    void set_degree(int degree);
private:
		Nurbs(const Nurbs &);
};

class NurbsSurface {

%TypeHeaderCode
#include <nurbssurface.h>
%End

public:
    NurbsSurface();
    void set_controls(QList<Vertex> new_controls_1, QList<Vertex> new_controls_2);
    //void addControls(QList<Vertex> newControls);
    double R(int i, int j, int n, float u, float v);
    Vertex S(float u, float v);
    QList<Vertex> range(int divisions1, int divisions2);
private:
		NurbsSurface(const NurbsSurface &);
};