//SIP wrapper to the NurbSurfer library.

%Module NurbSurfer

%Import QtCore/QtCoremod.sip

struct Vertex {

%TypeHeaderCode
#include <vertex.h>
%End

    double x;
    double y;
	  double z;
};


class Nurbs {

%TypeHeaderCode
#include <nurbs.h>
%End

public:
    Nurbs();
    void setControls(QList<Vertex> controls);
    Vertex C(double u);
    QList<Vertex> range(int divisions);
private:
		Nurbs(const Nurbs &);
};
